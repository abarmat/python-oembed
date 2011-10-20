Python-oembed
====

This library provides a pure python OEmbed consumer to get resources from OEmbed providers.

Based on reference from http://oembed.com/

oEmbed is a format for allowing an embedded representation of a URL on third party sites. The simple API allows a website to display embedded content (such as photos or videos) when a user posts a link to that resource, without having to parse the resource directly.

OEmbed format authors:

* Cal Henderson (cal at iamcal.com)
* Mike Malone (mjmalone at gmail.com)
* Leah Culver (leah.culver at gmail.com)
* Richard Crowley (r at rcrowley.org)

Install
------------

    pip install python-oembed

Use
------------

To create an instance of the oEmbed consumer:

    >>> import oembed
    >>> consumer = oembed.OEmbedConsumer()

To add a provider endpoint to this consumer: 

* The first parameter is the URL of the endpoint published by the provider.
* The second parameter is the URL schema to use with this endpoint.

For example:

    >>> endpoint = oembed.OEmbedEndpoint('http://www.flickr.com/services/oembed', ['http://*.flickr.com/*'])
    >>> consumer.addEndpoint(endpoint)

To get the provider response for a URL:

    >>> response = consumer.embed('http://www.flickr.com/photos/wizardbt/2584979382/')

To print the response results (each field can be read as a python dict, None if empty):

    >>> import pprint
    >>> pprint.pprint(response.getData())
    >>> print response['url']

To read the full documentation:

    $ pydoc oembed

Test
------------

    cd python-oembed
    python oembed_test.py

License
------------
Copyright (c) 2008 Ariel Barmat

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