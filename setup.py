# coding: utf-8

import sys
from setuptools import setup, find_packages

NAME = "ts-sdk-python"
VERSION = "1.0.0"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = [
    "boto3",
    "jsonschema",
    "typing-extensions",
    "query-string",
    "smart-open",
    "requests",
    "importlib-metadata",
    "urllib3"
    ]

setup(
    name=NAME,
    version=VERSION,
    description="",
    author_email="",
    url="",
    keywords=[],
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    long_description="""\
    ### Vocabulary Before you begin, please familiarize yourself with our [Glossary of Terms](https://riffyn.zendesk.com/hc/en-us/sections/203255778-Glossary-of-Terms-).  ### Getting Started If you&#39;d like to play around with the API, there are several free GUI tools that will allow you to send requests and receive responses. We suggest using the free app [Postman](https://www.getpostman.com/).    ### Authentication Begin with a call the [authenticate](/#api-Authentication-authenticate) endpoint using [HTTP Basic authentication](https://en.wikipedia.org/wiki/Basic_access_authentication) with your &#x60;username&#x60; and &#x60;password&#x60; to retrieve either an API Key or an Access Token. For example:      curl -X POST -u \&quot;&lt;username&gt;\&quot; https://app.riffyn.com/v1/auth -v  You may then use either the API Key or the accessToken for all future requests to the API. For example:      curl -H \&quot;access-token: &lt;ACCESS_TOKEN&gt;\&quot; https://app.riffyn.com/v1/units -v      curl -H \&quot;api-key: &lt;API_KEY&gt;\&quot; https://app.riffyn.com/v1/units -v  The tokens&#39; values will be either in the message returned by the &#x60;/authenticate&#x60; endpoint or in the createApiKey &#x60;/auth/api-key&#x60; or CreateAccesToken &#x60;/auth/access-token&#x60; endpoints. The API Key will remain valid until it is deauthorized by revoking it through the Security Settings in the Riffyn App UI. The API Key is best for running scripts and longer lasting interactions with the API. The Access Token will expire automatically and is best suited to granting applications short term access to the Riffyn API. Make your requests by sending the HTTP header &#x60;api-key: $API_KEY&#x60;, or &#x60;access-token: $ACCESS_TOKEN&#x60;. In Postman, add your prefered token to the headers under the Headers tab for any request other than the original request to &#x60;/authenticate&#x60;.  If you are enrolled in MultiFactor Authentication (MFA) the &#x60;status&#x60; returned by the &#x60;/authenticate&#x60; endpoint will be &#x60;MFA_REQUIRED&#x60;. A &#x60;passCode&#x60;, a &#x60;stateToken&#x60;, and a &#x60;factorId&#x60; must be passed to the [/verify](/#api-Authentication-verify) endpoint to complete the authentication process and achieve the &#x60;SUCCESS&#x60; status. MFA must be managed in the Riffyn App UI.  ### Paging and Sorting The majority of endpoints that return a list of data support paging and sorting through the use of three properties, &#x60;limit&#x60;,  &#x60;offset&#x60;, and &#x60;sort&#x60;. Please see the list of query parameters, displayed below each endpoint&#39;s code examples, to see if paging or sorting is supported for that specific endpoint.  Certain endpoints return data that&#39;s added frequently, like resources. As a result, you may want filter results on either the maximum or minimum creation timestamp. This will prevent rows from shifting their position from the top of the list, as you scroll though subsequent pages of a multi-page response.  Before querying for the first page, store the current date-time (in memory, a database, a file...). On subsequent pages you *may* include the &#x60;before&#x60; query parameter, to limit the results to records created before that date-time. E.g. before loading page one, you store the current date time of &#x60;2016-10-31T22:00:00Z&#x60; (ISO date format). Later, when generating the URL for page two, you *could* limit the results by including the query parameter &#x60;before&#x3D;1477951200000&#x60; (epoch timestamp).  ### Client SDKs You may write your own API client, or you may use one of ours. [Click here](/clients) to select your programming language and download an API client.
    """
)
