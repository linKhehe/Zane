async def get_last_message(channel, message):
    async for message in channel.history(limit=10, before=message):
        if message.content is not None:
            return message
    return None
