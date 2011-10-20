import unittest
import urllib2
import oembed


class EndpointTest(unittest.TestCase):
    def testInit(self):
        #plain init
        ep = oembed.OEmbedEndpoint('http://www.flickr.com/services/oembed')
        self.assertEqual(len(ep.getUrlSchemes()), 0)
                
        #init with schemes
        ep = oembed.OEmbedEndpoint('http://www.flickr.com/services/oembed',\
                                   ['http://*.flickr.com/*',\
                                    'http://flickr.com/*'])
        self.assertEqual(len(ep.getUrlSchemes()), 2)
        
    def testUrlScheme(self):
        ep = oembed.OEmbedEndpoint('http://www.flickr.com/services/oembed')
   
        #add some schemes
        ep.addUrlScheme('http://flickr.com/*')
        ep.addUrlScheme('http://*.flickr.com/*')
        self.assertEqual(len(ep.getUrlSchemes()), 2)

        #add duplicated
        ep.addUrlScheme('http://*.flickr.com/*')
        self.assertEqual(len(ep.getUrlSchemes()), 2)

        #remove url
        ep.addUrlScheme('http://*.flickr.com/')
        ep.delUrlScheme('http://flickr.com/*')
        self.assertEqual(len(ep.getUrlSchemes()), 2)
        
        #clear all
        ep.clearUrlSchemes()
        self.assertEqual(len(ep.getUrlSchemes()), 0)
        
class UrlSchemeTest(unittest.TestCase):
    def testInit(self):
        scheme = oembed.OEmbedUrlScheme('http://*.flickr.com/*')

        self.assertEqual(scheme.getUrl(), 'http://*.flickr.com/*')
        
        self.assertTrue(scheme.match('http://www.flickr.com/photos/wizardbt/2584979382/'))
        self.assertFalse(scheme.match('http://flickr.com/photos/wizardbt/2584979382/'))
        self.assertFalse(scheme.match('http://flick.com/photos/wizardbt/2584979382/'))
        self.assertFalse(scheme.match('https://flickr.com/photos/wizardbt/2584979382/'))
        self.assertFalse(scheme.match('flickr.com/photos/wizardbt/2584979382/'))
        self.assertFalse(scheme.match('http://flickr/photos/wizardbt/2584979382/'))
        self.assertFalse(scheme.match('http://conflickr.com/'))
      
class ConsumerTest(unittest.TestCase):
    def testGettersAndSetters(self):
        consumer = oembed.OEmbedConsumer()
        
        ep1 = oembed.OEmbedEndpoint('http://www.flickr.com/services/oembed')
        ep2 = oembed.OEmbedEndpoint('http://api.pownce.com/2.1/oembed.{format}')
        ep3 = oembed.OEmbedEndpoint('http://www.vimeo.com/api/oembed.{format}')
        
        #adding
        consumer.addEndpoint(ep1)
        consumer.addEndpoint(ep2)
        consumer.addEndpoint(ep3)
        self.assertEqual(len(consumer.getEndpoints()), 3)
        
        #removing one
        consumer.delEndpoint(ep2)
        self.assertEqual(len(consumer.getEndpoints()), 2)

        #clearing all!
        consumer.clearEndpoints()
        self.assertEqual(len(consumer.getEndpoints()), 0)
        
    def testEmbed(self):
        consumer = oembed.OEmbedConsumer()
  
        ep1 = oembed.OEmbedEndpoint('http://www.flickr.com/services/oembed')
        ep1.addUrlScheme('http://*.flickr.com/*')        
    
        ep2 = oembed.OEmbedEndpoint('http://api.pownce.com/2.1/oembed.{format}')
        ep2.addUrlScheme('http://*.pownce.com/*')        
  
        consumer.addEndpoint(ep1)
        consumer.addEndpoint(ep2)
        
        #invalid format        
        self.assertRaises(oembed.OEmbedInvalidRequest, consumer.embed, \
                          'http://www.flickr.com/photos/wizardbt/2584979382/', \
                          format='text')
        
        #no matching endpoint for the url
        self.assertRaises(oembed.OEmbedNoEndpoint, consumer.embed, \
                          'http://google.com/123456')

    def testResponses(self):
        consumer = oembed.OEmbedConsumer()
      
        ep = oembed.OEmbedEndpoint('http://www.flickr.com/services/oembed')
        ep.addUrlScheme('http://*.flickr.com/*')            
  
        consumer.addEndpoint(ep)

        #json
        resp = consumer.embed('http://www.flickr.com/photos/wizardbt/2584979382/', 
                              format='json')
        #xml
        resp = consumer.embed('http://www.flickr.com/photos/wizardbt/2584979382/', 
                              format='xml')

        #resource not found
        self.assertRaises(urllib2.HTTPError, consumer.embed, \
                          'http://www.flickr.com/photos/wizardbt/', \
                          format='json')
                          
    def testNoEndpoints(self):
        consumer = oembed.OEmbedConsumer()        

        self.assertRaises(oembed.OEmbedNoEndpoint, consumer.embed, \
                          'http://www.flickr.com/photos/wizardbt/2584979382/')
        
    def testBrokenEndpoint(self):
        consumer = oembed.OEmbedConsumer()
    
        ep = oembed.OEmbedEndpoint('http://localhost')
        ep.addUrlScheme('http://localhost/*')
        consumer.addEndpoint(ep)
    
        self.assertRaises(urllib2.URLError, consumer.embed, \
                          'http://localhost/test')


def suite():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(EndpointTest))
    suite.addTests(unittest.makeSuite(UrlSchemeTest))
    suite.addTests(unittest.makeSuite(ConsumerTest))
    return suite


if __name__ == '__main__':
    unittest.main()