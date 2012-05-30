'''A Python library that implements an OEmbed consumer to use with OEmbed providers.

Based on reference from http://oembed.com/

oEmbed is a format for allowing an embedded representation of a URL on 
third party sites. The simple API allows a website to display embedded content 
(such as photos or videos) when a user posts a link to that resource, without 
having to parse the resource directly.

OEmbed format authors:
    * Cal Henderson (cal [at] iamcal.com)
    * Mike Malone (mjmalone [at] gmail.com)
    * Leah Culver (leah.culver [at] gmail.com)
    * Richard Crowley (r [at] rcrowley.org)


Simple usage:

    import oembed

    consumer = oembed.OEmbedConsumer()
    endpoint = oembed.OEmbedEndpoint('http://www.flickr.com/services/oembed', 
                                    ['http://*.flickr.com/*'])
    consumer.addEndpoint(endpoint)

    response = consumer.embed('http://www.flickr.com/photos/wizardbt/2584979382/')

    print response['url']

    import pprint
    pprint.pprint(response.getData())


Copyright (c) 2008 Ariel Barmat, abarmat@gmail.com

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE

'''

import urllib
import urllib2
import re

# json module is in the standard library as of python 2.6; fall back to
# simplejson if present for older versions.
try:
    import json
    assert hasattr(json, "loads") and hasattr(json, "dumps")
    json_decode = json.loads
    json_encode = json.dumps
except Exception:
    try:
        import simplejson
        json_decode = lambda s: simplejson.loads(_unicode(s))
        json_encode = lambda v: simplejson.dumps(v)
    except ImportError:
        try:
            # For Google AppEngine
            from django.utils import simplejson
            json_decode = lambda s: simplejson.loads(_unicode(s))
            json_encode = lambda v: simplejson.dumps(v)
        except ImportError:
            def json_decode(s):
                raise NotImplementedError(
                    "A JSON parser is required, e.g., simplejson at "
                    "http://pypi.python.org/pypi/simplejson/")
            json_encode = json_decode
            
try:
    from xml.etree import cElementTree as etree
except ImportError:
    # Running Python < 2.4 so we need a different import
    import cElementTree as etree


class OEmbedError(Exception):
    '''Base class for OEmbed errors'''

class OEmbedInvalidRequest(OEmbedError):
    '''Raised when an invalid parameter is used in a request'''
    
class OEmbedNoEndpoint(OEmbedError):
    '''Raised when no endpoint is available for a particular URL'''


class OEmbedResponse(object):
    '''
    Base class for all OEmbed responses. 
    
    This class provides a factory of OEmbed responses according to the format
    detected in the type field. It also validates that mandatory fields are 
    present.
    '''           
    def _validateData(self, data):
        pass
               
    def __getitem__(self, name):
        return self._data.get(name)
    
    def getData(self):
        return self._data
        
    def loadData(self, data):
        self._validateData(data) 
        self._data = data

    @classmethod
    def createLoad(cls, data):
        if not data.has_key('type') or \
           not data.has_key('version'):
            raise OEmbedError('Missing required fields on OEmbed response.')
        response = cls.create(data['type'])
        response.loadData(data)       
        return response

    @classmethod
    def create(cls, responseType):
        return resourceTypes.get(responseType, OEmbedResponse)()

    @classmethod
    def newFromJSON(cls, raw):
        data = json_decode(raw)
        return cls.createLoad(data)
        
    @classmethod
    def newFromXML(cls, raw):
        elem = etree.XML(raw)
        data = dict([(e.tag, e.text) for e in elem.getiterator() \
                    if e.tag not in ['oembed']])        
        return cls.createLoad(data)
    
        
class OEmbedPhotoResponse(OEmbedResponse):
    '''
    This type is used for representing static photos. 
    '''
    def _validateData(self, data):
        OEmbedResponse._validateData(self, data)
    
        if not data.has_key('url') or \
           not data.has_key('width') or \
           not data.has_key('height'):
            raise OEmbedError('Missing required fields on OEmbed photo response.')        

class OEmbedVideoResponse(OEmbedResponse):
    '''
    This type is used for representing playable videos.    
    '''
    def _validateData(self, data):
        OEmbedResponse._validateData(self, data)

        if not data.has_key('html') or \
           not data.has_key('width') or \
           not data.has_key('height'):
            raise OEmbedError('Missing required fields on OEmbed video response.')        

class OEmbedLinkResponse(OEmbedResponse):
    '''
    Responses of this type allow a provider to return any generic embed data 
    (such as title and author_name), without providing either the url or html 
    parameters. The consumer may then link to the resource, using the URL 
    specified in the original request.
    '''

class OEmbedRichResponse(OEmbedResponse):
    '''
    This type is used for rich HTML content that does not fall under 
    one of the other categories.
    ''' 
    def _validateData(self, data):
        OEmbedResponse._validateData(self, data)

        if not data.has_key('html') or \
           not data.has_key('width') or \
           not data.has_key('height'):
            raise OEmbedError('Missing required fields on OEmbed rich response.')     


resourceTypes = {
    'photo': OEmbedPhotoResponse,
    'video': OEmbedVideoResponse,
    'link':  OEmbedLinkResponse,
    'rich':  OEmbedRichResponse
}

class OEmbedEndpoint(object):
    '''
    A class representing an OEmbed Endpoint exposed by a provider.
    
    This class handles a number of URL schemes and manage resource retrieval.    
    '''

    def __init__(self, url, urlSchemes=None):
        '''
        Create a new OEmbedEndpoint object. 
        
        Args:
            url: The url of a provider API (API endpoint).
            urlSchemes: A list of URL schemes for this endpoint. 
        '''
        self._urlApi = url
        self._urlSchemes = {}
        self._initRequestHeaders()
        self._urllib = urllib2

        if urlSchemes is not None:
            map(self.addUrlScheme, urlSchemes)

        self._implicitFormat = self._urlApi.find('{format}') != -1
        
    def _initRequestHeaders(self):
        self._requestHeaders = {}
        self.setUserAgent('python-oembed')

    def addUrlScheme(self, url):
        '''
        Add a url scheme to this endpoint. It takes a url string and create
        the OEmbedUrlScheme object internally.
        
        Args:
            url: The url string that represents a url scheme to add.
        '''
        #@TODO: validate invalid url format according to http://oembed.com/
        if not isinstance(url, str):
            raise TypeError('url must be a string value')
        
        if not self._urlSchemes.has_key(url):
            self._urlSchemes[url] = OEmbedUrlScheme(url)
    
    def delUrlScheme(self, url):
        '''
        Remove an OEmbedUrlScheme from the list of schemes.
        
        Args:
           url: The url used as key for the urlSchems dict. 
        '''
        if self._urlSchemes.has_key(url):
            del self._urlSchemes[url]
    
    def clearUrlSchemes(self):
        '''Clear the schemes in this endpoint.'''
        self._urlSchemes.clear()
            
    def getUrlSchemes(self):
        '''
        Get the url schemes in this endpoint. 
        
        Returns:
            A dict of OEmbedUrlScheme objects. k => url, v => OEmbedUrlScheme
        '''    
        return self._urlSchemes

    def match(self, url):
        '''
        Try to find if url matches against any of the schemes within this 
        endpoint.

        Args:
            url: The url to match against each scheme
            
        Returns:
            True if a matching scheme was found for the url, False otherwise
        '''
        for urlScheme in self._urlSchemes.itervalues():
            if urlScheme.match(url):
                return True
        return False
        
    def request(self, url, **opt):
        '''
        Format the input url and optional parameters, and provides the final url 
        where to get the given resource. 
        
        Args:
            url: The url of an OEmbed resource.
            **opt: Parameters passed to the url.
            
        Returns:
            The complete url of the endpoint and resource.
        '''
        params = opt
        params['url'] = url        
        urlApi = self._urlApi
        
        if params.has_key('format') and self._implicitFormat:
            urlApi = self._urlApi.replace('{format}', params['format'])
            del params['format']
                
        if '?' in urlApi:
            return "%s&%s" % (urlApi, urllib.urlencode(params))
        else:
            return "%s?%s" % (urlApi, urllib.urlencode(params))

    def get(self, url, **opt):
        '''
        Convert the resource url to a complete url and then fetch the 
        data from it.
        
        Args:
            url: The url of an OEmbed resource.
            **opt: Parameters passed to the url.
            
        Returns:
            OEmbedResponse object according to data fetched
        '''
        return self.fetch(self.request(url, **opt))

    def fetch(self, url):
        '''
        Fetch url and create a response object according to the mime-type.
        
        Args:
            url: The url to fetch data from
            
        Returns:
            OEmbedResponse object according to data fetched
        '''        
        opener = self._urllib.build_opener()
        opener.addheaders = self._requestHeaders.items()
        response = opener.open(url)
        headers = response.info()
        raw = response.read()

        if not headers.has_key('Content-Type'):
            raise OEmbedError('Missing mime-type in response')
        
        if headers['Content-Type'].find('application/xml') != -1 or \
           headers['Content-Type'].find('text/xml') != -1:
            response = OEmbedResponse.newFromXML(raw)
        elif headers['Content-Type'].find('application/json') != -1 or \
             headers['Content-Type'].find('text/json') != -1:
            response = OEmbedResponse.newFromJSON(raw)
        else:
            raise OEmbedError('Invalid mime-type in response - %s' % headers['Content-Type'])

        return response

    def setUrllib(self, urllib):
        '''
        Override the default urllib implementation.

        Args:
            urllib: an instance that supports the same API as the urllib2 module
        '''
        self._urllib = urllib

    def setUserAgent(self, user_agent):
        '''
        Override the default user agent

        Args:
            user_agent: a string that should be send to the server as the User-agent
        '''
        self._requestHeaders['User-Agent'] = user_agent


class OEmbedUrlScheme(object):
    '''
    A class representing an OEmbed URL schema.
    '''

    def __init__(self, url):
        '''
        Create a new OEmbedUrlScheme instance. 
        
        Args;
            url: The url scheme. It also takes the wildcard character (*).
        '''
        self._url = url
        if url.startswith('regex:'):
            self._regex = re.compile(url[6:])
        else:
            self._regex = re.compile(url.replace('.', '\.')\
                                     .replace('*', '.*'))
            
    def getUrl(self):
        '''
        Get the url scheme.
        
        Returns:
            The url scheme.
        '''
        return self._url

    def match(self, url):
        '''
        Match the url against this scheme.

        Args:
            url: The url to match against this scheme.
            
        Returns:
            True if a match was found for the url, False otherwise
        '''
        return self._regex.match(url) is not None

    def __repr__(self):
        return "%s - %s" % (object.__repr__(self), self._url)


class OEmbedConsumer(object):
    '''
    A class representing an OEmbed consumer.
    
    This class manages a number of endpoints, selects the corresponding one 
    according to the resource url passed to the embed function and fetches
    the data.
    '''    
    def __init__(self):
        self._endpoints = []
    
    def addEndpoint(self, endpoint):
        '''
        Add a new OEmbedEndpoint to be manage by the consumer.
        
        Args:
            endpoint: An instance of an OEmbedEndpoint class.
        '''
        self._endpoints.append(endpoint)

    def delEndpoint(self, endpoint):
        '''
        Remove an OEmbedEnpoint from this consumer.
        
        Args:
            endpoint: An instance of an OEmbedEndpoint class.
        '''    
        self._endpoints.remove(endpoint)
        
    def clearEndpoints(self):
        '''Clear all the endpoints managed by this consumer.'''
        del self._endpoints[:]

    def getEndpoints(self):
        '''
        Get the list of endpoints.
        
        Returns:
            The list of endpoints in this consumer.
        '''
        return self._endpoints

    def _endpointFor(self, url):
        for endpoint in self._endpoints:
            if endpoint.match(url):
                return endpoint
        return None
        
    def _request(self, url, **opt):
        endpoint = self._endpointFor(url)
        if endpoint is None:
            raise OEmbedNoEndpoint('There are no endpoints available for %s' % url)        
        return endpoint.get(url, **opt)
                    
    def embed(self, url, format='json', **opt):
        '''
        Get an OEmbedResponse from one of the providers configured in this 
        consumer according to the resource url.
        
        Args:
            url: The url of the resource to get.
            format: Desired response format.
            **opt: Optional parameters to pass in the url to the provider.
        
        Returns:
            OEmbedResponse object.
        '''
        if format not in ['json', 'xml']:
            raise OEmbedInvalidRequest('Format must be json or xml')        
        opt['format'] = format
        return self._request(url, **opt)

def _unicode(value):
    if isinstance(value, str):
        return value.decode("utf-8")
    assert isinstance(value, unicode)
    return value