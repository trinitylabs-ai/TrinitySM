"""Runtime compatibility fixes for the local vLLM environment."""

import importlib
import ipaddress
import socket

import torch
from vllm.model_executor.layers.quantization.modelopt import ModelOptQuantConfigBase
from vllm.model_executor.layers.vocab_parallel_embedding import (
    ParallelLMHead,
    UnquantizedEmbeddingMethod,
)


_original_get_quant_method = ModelOptQuantConfigBase.get_quant_method


def _get_quant_method_with_tied_lm_head(self, layer, prefix):
    if self.is_layer_excluded(prefix) and isinstance(layer, ParallelLMHead):
        return UnquantizedEmbeddingMethod()
    return _original_get_quant_method(self, layer, prefix)


ModelOptQuantConfigBase.get_quant_method = _get_quant_method_with_tied_lm_head


_rendezvous = importlib.import_module("torch.distributed.rendezvous")
_original_create_c10d_store = _rendezvous._create_c10d_store


def _is_loopback(hostname):
    try:
        return ipaddress.ip_address(hostname).is_loopback
    except ValueError:
        return hostname == "localhost"


def _create_loopback_c10d_store(
    hostname,
    port,
    rank,
    world_size,
    timeout,
    use_libuv=True,
):
    """Prebind rank-zero TCPStore sockets when vLLM selected loopback."""

    if (
        rank != 0
        or not _is_loopback(hostname)
        or _rendezvous._torchelastic_use_agent_store()
    ):
        return _original_create_c10d_store(
            hostname,
            port,
            rank,
            world_size,
            timeout,
            use_libuv,
        )

    family = socket.AF_INET6 if ":" in hostname else socket.AF_INET
    listen_socket = socket.socket(family, socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_socket.bind((hostname, port))
    listen_socket.listen()
    bound_port = listen_socket.getsockname()[1]
    listen_fd = listen_socket.detach()
    try:
        return torch.distributed.TCPStore(
            host_name=hostname,
            port=bound_port,
            world_size=world_size,
            is_master=True,
            timeout=timeout,
            multi_tenant=True,
            master_listen_fd=listen_fd,
            use_libuv=False,
        )
    except Exception:
        socket.close(listen_fd)
        raise


_rendezvous._create_c10d_store = _create_loopback_c10d_store
