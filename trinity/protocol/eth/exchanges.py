from typing import (
    Any,
    Dict,
    Sequence,
    Tuple,
)

from eth_typing import (
    BlockIdentifier,
    Hash32,
)
from eth.abc import BlockHeaderAPI

from trinity.protocol.common.exchanges import (
    BaseExchange,
)
from trinity.protocol.common.normalizers import (
    NoopNormalizer,
)
from trinity.protocol.common.validators import (
    noop_payload_validator,
)
from trinity.protocol.common.types import (
    BlockBodyBundles,
    NodeDataBundles,
    ReceiptsByBlock,
    ReceiptsBundles,
)
from trinity.rlp.block_body import BlockBody

from .normalizers import (
    GetBlockBodiesNormalizer,
    GetNodeDataNormalizer,
    ReceiptsNormalizer,
)
from .requests import (
    GetBlockBodiesRequest,
    GetBlockHeadersRequest,
    GetNodeDataRequest,
    GetReceiptsRequest,
)
from .trackers import (
    GetBlockHeadersTracker,
    GetBlockBodiesTracker,
    GetNodeDataTracker,
    GetReceiptsTracker
)
from .validators import (
    GetBlockBodiesValidator,
    GetBlockHeadersValidator,
    GetNodeDataValidator,
    ReceiptsValidator,
)

BaseGetBlockHeadersExchange = BaseExchange[
    Dict[str, Any],
    Sequence[BlockHeaderAPI],
    Tuple[BlockHeaderAPI, ...],
]


class GetBlockHeadersExchange(BaseGetBlockHeadersExchange):
    _normalizer = NoopNormalizer[Sequence[BlockHeaderAPI], Tuple[BlockHeaderAPI, ...]]()
    request_class = GetBlockHeadersRequest
    tracker_class = GetBlockHeadersTracker

    async def __call__(  # type: ignore
            self,
            block_number_or_hash: BlockIdentifier,
            max_headers: int = None,
            skip: int = 0,
            reverse: bool = True,
            timeout: float = None) -> Tuple[BlockHeaderAPI, ...]:

        original_request_args = (block_number_or_hash, max_headers, skip, reverse)
        validator = GetBlockHeadersValidator(*original_request_args)
        request = self.request_class(*original_request_args)

        return await self.get_result(
            request,
            self._normalizer,
            validator,
            noop_payload_validator,
            timeout,
        )


BaseNodeDataExchange = BaseExchange[Sequence[Hash32], Sequence[bytes], NodeDataBundles]


class GetNodeDataExchange(BaseNodeDataExchange):
    _normalizer = GetNodeDataNormalizer()
    request_class = GetNodeDataRequest
    tracker_class = GetNodeDataTracker

    async def __call__(self,  # type: ignore
                       node_hashes: Sequence[Hash32],
                       timeout: float = None) -> NodeDataBundles:
        validator = GetNodeDataValidator(node_hashes)
        request = self.request_class(node_hashes)
        return await self.get_result(
            request,
            self._normalizer,
            validator,
            noop_payload_validator,
            timeout,
        )


class GetReceiptsExchange(BaseExchange[Sequence[Hash32], ReceiptsByBlock, ReceiptsBundles]):
    _normalizer = ReceiptsNormalizer()
    request_class = GetReceiptsRequest
    tracker_class = GetReceiptsTracker

    async def __call__(self,  # type: ignore
                       headers: Sequence[BlockHeaderAPI],
                       timeout: float = None) -> ReceiptsBundles:
        validator = ReceiptsValidator(headers)

        block_hashes = tuple(header.hash for header in headers)
        request = self.request_class(block_hashes)

        return await self.get_result(
            request,
            self._normalizer,
            validator,
            noop_payload_validator,
            timeout,
        )


BaseGetBlockBodiesExchange = BaseExchange[
    Sequence[Hash32],
    Sequence[BlockBody],
    BlockBodyBundles,
]


class GetBlockBodiesExchange(BaseGetBlockBodiesExchange):
    _normalizer = GetBlockBodiesNormalizer()
    request_class = GetBlockBodiesRequest
    tracker_class = GetBlockBodiesTracker

    async def __call__(self,  # type: ignore
                       headers: Sequence[BlockHeaderAPI],
                       timeout: float = None) -> BlockBodyBundles:
        validator = GetBlockBodiesValidator(headers)

        block_hashes = tuple(header.hash for header in headers)
        request = self.request_class(block_hashes)

        return await self.get_result(
            request,
            self._normalizer,
            validator,
            noop_payload_validator,
            timeout,
        )
