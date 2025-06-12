
import logging
import time
import redis
from redis.exceptions import RedisError

from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

REDIS_HOST = "docker-wxo-server-redis-1"
REDIS_PORT = 6379

@tool
def publish_message(channel: str = "ASSISTANTS", message: str = "Its Working"):
    """
    This tool is used to publish message to the given channel.

    :param channel: Redis channel to publish the message.
    :param message: This is the message that needs to be published

    :returns: A success message or an error message.

    """   
    logger.info(f"\n\n--------- IN PUBLISHER TOOL, channel: {channel}-----------, \nmessage: {message} \n---------------- \n\n")
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        rcvd = r.publish(channel, message)
        logger.info(f"\n\n--------- IN PUBLISHER TOOL, RESULT: {channel}-----------\n\n")
        if rcvd > 0:
            # return {"result": "Message published successfully"}
            return f"Message published to channel '{channel}'."
        else:
            return f"ERROR: Message publish to channel: {channel} FAILED"
    except RedisError as e:
        logger.error(e)
        return f"Error while publishing message to channel '{channel}': {str(e)}"
    except Exception as e:
        logger.error(e)
        return f"ERROR: Message publish to channel: {channel} FAILED"
    finally:
        r.close()
    

@tool
def subscribe_to_channel(channel: str = "AGENTS", func: any = None):
    """
    This tool is used by the Agents to subscribe for messages published to the given channel.

    :params channel: Channel to subscribe, for the published messages.
    :params func: This is a callback function which will be called by passing the message.  This function implementation is handled by the tool calling Agent.

    """
    logger.info(f"\n\n--------- IN SUBSCRIBER TOOL, channel: {channel} ------------ \n\n")
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
    try:
        p = r.pubsub(ignore_subscribe_messages=True)
        p.subscribe(channel)
        logger.info(f"Subscribed to {channel}. Waiting for messages...")
        for message in p.listen():
            if message['type'] == 'message':
                logger.info(f"Received: {message['data']}")
                if func is not None:
                    func(message)
                # message = p.get_message()
    except redis.exceptions.ConnectionError as e:
        logger.error(f"Connection Error: {e}")
        time.sleep(3)
        p = r.pubsub()
        p.subscribe(channel)
    except redis.exceptions.AuthenticationError as e:
        logger.error(f"Authentication Error: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    if message:
        logger.info(message)
        time.sleep(0.001)
    


