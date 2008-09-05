import oembed

consumer = oembed.OEmbedConsumer()
endpoint = oembed.OEmbedEndpoint('http://www.flickr.com/services/oembed', \
                                 ['http://*.flickr.com/*'])
consumer.addEndpoint(endpoint)

response = consumer.embed('http://www.flickr.com/photos/wizardbt/2584979382/')

print response['url']

import pprint
pprint.pprint(response.getData())
