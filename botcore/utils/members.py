"""Useful helper functions for interactin with :obj:`discord.Member` objects."""

import typing

import discord

from botcore.utils import logging

log = logging.get_logger(__name__)


async def get_or_fetch_member(guild: discord.Guild, member_id: int) -> typing.Optional[discord.Member]:
    """
    Attempt to get a member from cache; on failure fetch from the API.

    Returns:
        The :obj:`discord.Member` or :obj:`None` to indicate the member could not be found.
    """
    if member := guild.get_member(member_id):
        log.trace(f"{member} retrieved from cache.")
    else:
        try:
            member = await guild.fetch_member(member_id)
        except discord.errors.NotFound:
            log.trace(f"Failed to fetch {member_id} from API.")
            return None
        log.trace(f"{member} fetched from API.")
    return member


async def handle_role_change(
    member: discord.Member,
    coro: typing.Callable[..., typing.Coroutine],
    role: discord.Role
) -> None:
    """
    Await the given ``coro`` with ``member`` as the sole argument.

    Handle errors that we expect to be raised from
    :obj:`discord.Member.add_roles` and :obj:`discord.Member.remove_roles`.

    Args:
        member: The member to pass to ``coro``.
        coro: This is intended to be :obj:`discord.Member.add_roles` or :obj:`discord.Member.remove_roles`.
    """
    try:
        await coro(role)
    except discord.NotFound:
        log.error(f"Failed to change role for {member} ({member.id}): member not found")
    except discord.Forbidden:
        log.error(
            f"Forbidden to change role for {member} ({member.id}); "
            f"possibly due to role hierarchy"
        )
    except discord.HTTPException as e:
        log.error(f"Failed to change role for {member} ({member.id}): {e.status} {e.code}")
