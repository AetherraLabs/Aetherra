# TODO: For backward compatibility, we are importing the public objects
# originally from this file.
from torch.distributed.fsdp import (  # noqa: F401
    FSDPModule,
    UnshardHandle,
    fully_shard,
    register_fsdp_forward_method,
)
