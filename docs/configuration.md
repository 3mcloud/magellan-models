# Configuration via MagellanConfig

Utilizing Magellan requires providing your own Configuration instance. For example:

`models, funcs, config = initialize_with_endpoint(my_endpoint, my_configuration)`

In this situation, `my_configuration` is an instance of a MagellanConfig (or an instance of something inheriting from MagellanConfig).

To override any of the default aspects of a MagellanConfig instance, you'll want to import the config, initialize an instance, and then override any attributes or functions:

```python
from magellan_models.config import MagellanConfig
conf = MagellanConfig()
conf.api_endpoint = "https://myAPIPath/api/v1"
conf.requests_args = {"retry_limit": 50}
```

The rest of this documentation goes into detail about what attributes and functions are user customizable inside of the MagellanConfig class.

## Attributes

### jwt: `str`

The Configuration JWT allows for a jwt token to be stored for a set of models via a configuration setting. This value defaults to an empty string ("") and can be left alone if you override the header generation function. 

### api_endpoint: `str`

The `api_endpoint` attribute is a string that stores the API url that the Magellan models are associated with. The final slash ("/") in the url should be removed. The idea being that a GET call to `f"{conf.api_endpoint}/samples` should be the same as a GET list call to the samples resource url.

This attribute will **almost always** need to be overwritten by a user.

### id_separator: `str`

The `id_separator` attribute is a string value indicating the separator used in the paths for singular get requests. For example if I had a sample with id=123, I'd want to do a GET request to `{api_endpoint}/sample/123`. For a given openAPI spec, the path might actually be written as `{api_endpoint}/sample/{id_}` or `{api_endpoint}/sample/{identifier}` etc. The **id_separator should be a regex pattern** that is later nested by the openAPI parser into a larger regular expression to do route matching with. This lets you define a regex to support multiple ID separators as you'd like. By default this value is `"\{id_\}"`.

### function_naming_style: `str`

function_naming_style has to be either "raw" or "pretty" and defines what naming convention is used for the non-model route functions generated. For example a GET call to /healthcheck would be converted to "GET /healthcheck" or "get_from_healthcheck" depending on which naming convention you use. For routes with parameters the scheming follows this convention: raw: "GET /echo/{message}", pretty: "get_from_echo_with_message". The functions themselves have no changes in terms of functionality.

## experimental_functions: 'bool'

Sets if Experimental Functionality is enabled or not. Defaults to 'False'.

### requests_args: `dict`

Magellan uses the `requests` module by default underneath the Model "orm". For any given request, you can also pass in any requests module specific arguments as well. The configuration stores these arguments as a dict which is then unpacked whenever utilizing the requests module to make requests. By default this dict is empty (`{}`).

### print_on_init: `bool`

A simple boolean value designed to toggle whether or not the initialization function prints out helpful messages regarding which models and functions are generated. This value defaults to True.

### validation_output: `str`

Magellan will validate request bodies for the non-rest route functions. By default if the request_body has errors in its validation, a `MagellanRuntimeWarning` will be emitted. You can set the options for `validation_output` to either be `"warning"` or `"exception"`. Alternatively set this value to anything else (even `None`!) and skip validation messaging entirely.

### header_args_separator: `str`

If you want to define a way to set up header values for an HTTP request on a request basis, you can define a specific `header_args_separator` which will let Magellan know to forward any kwargs with a key value matching the value of the separator to the header generation function. Say for example I wanted to set the JWT on each query, and had a header function that accepts a token as a string and generates the HTTP header I desire. I can specify my header_args_separator to be "token_val", and then later do a request like this `MagModel.where(title="Chicken Nuggets", token_val=my_jwt)`. Here `my_jwt` is passed to the header generator function and plucked out of kwargs before any additional filter generation takes place. By default this value is 'header_args'.

### schema_attributes_path: `tuple`

The `schema_attributes_path` is a tuple or other iterable which stores the path to traverse an HTTP response definition in the OpenAPI schema. This path is followed down, and whatever object is at the end of that path is then the template to pull attributes from. By default this value matches the json::api specification with a value of `("properties", "data", "properties", "attributes", "properties")`. 

### schema_relationships_path: `tuple`

Similar to `schema_attributes_path` but instead related to a separate entity that stores relationship data. This is where relationships will be matched via their key names to see if Magellan can automatically generate helper functions as well. The default value is `("properties", "data", "properties", "relationships", "properties")`.

### model_attributes_path: `tuple`

Each model instance has its own representation. This representation is a dictionary object that stores attribute and relationships values. If you want to have a nested place to store the attribute values you can specify so here. For the purposes of default values, the MagellanConfig defaults to using `("attributes",)`.

### model_relationships_path: `tuple`

This is similar to the `model_attributes_path` value and the default value in this case is `("relationships",)`.

### params_args: `Iterable(str)`

A list of argument keys to pull out of the `kwargs` when creating parameters (see `create_params()` below). The arguments specified here should be pulled out before the remaining kwargs are sent to the `create_filters()` function. Defaults to `["sort"]`

### disabled_functions: `Iterable(str)`

An iterable of function names that you want to have be disabled for each Magellan model instance. This is useful if you want to disable `post` or `patch` functionality manually for whatever reason or block access to attributes that the parser may generate helper class functions for. Each function name specified will by default just raise a MagellanRuntimeException with a "This Function has been disabled" error message. Default value: `[]`.

## Functions

The Magellan Config also stores a host of helper functions that provide data conversion between the Magellan Models and the API that's being contacted.

### create_header(self, **kwargs) -> `dict`

The `create_header` function returns an HTTP request header utilizing whatever kwargs are passed in. By default, this header is just `{"authorizationtoken": f'Bearer {self.jwt}'}` but you can configure it to accept multiple arguments and also return whatever formatting you want. This header will be passed into the request whenever the API is called.

### create_filters(self, filtering_arguments: dict = {}, **kwargs) -> `dict`

The `create_filters` function transforms any filters defined by the user into a format that the API expects. By default this function tries to mimic the behavior of the flask-rest-jsonapi https://flask-rest-jsonapi.readthedocs.io/en/latest/filtering.html. Note, because APIs can expect different filtering keys (for example hitting /pets?filter[name]="Fido"&filter[year_of_birth]=2020 versus hitting /pets?filter={"op": "eq", "name": "title", "val": "Fido"}), the create_filters function needs to wrap whatever filters are generated with their own key. For example you might want to return something like this {"filter[name]": "fido", "filter[year_of_birth]: 2020} if your API won't accept the "filters" keyword.

### create_params(self, limit: int=None, **kwargs) -> `dict`

Generates the params value to pass to the requests package a limit value, and arbitrary kwargs. Traditionally this function will be in charge of also calling `create_filters`. As such, overriding it should ensure that filters are created and any additional logic is also properly implemented.

This function needs to pull out any value in the `params_args` attribute above from kwargs
Then kwargs need to be passed to `create_filters` in order to generate any filters in params
Finally if you have additional params to set up, you can add them to the output dict before returning the resulting params.

### api_response_to_representation(self, payload: dict) -> `dict`

The `api_response_to_representation` function takes in a payload (often a server response) and converts that to whatever dict formatting a Model's representation follows. By default this involves just returning the "data" attribute value of the payload. 

### representation_to_api(self, representation: dict) -> `dict`

The `representation_to_api` function takes in a representation dict and then maps it into the format that the API expects. By default this function just nests the representation under the key "data" (a la `lambda rep: {"data": rep}`).

### relationship_id_to_json_entry(self, relationship_id: str, **kwargs) -> `Union[dict, str]`

The `relationship_id_to_json_entry` function converts a given UUID or str into the format that the representation should store that element as. JSON:API relationship values tend to map as objects `{"id": myUUID, "type": myClass}` and the function by default converts IDs into that format with a passed in kwarg "relationship_type" to indicate class.

### get_list_from_resp(self, json_resp: dict) -> `list`

The `get_list_from_resp` function is called after a GET MANY request that returns a list of entities. In this instance if the list is nested in some other key (namely "data") then this function returns the value inside that key.

### get_next_link_from_resp(self, request_resp) -> `Union[str, bool]`

The `get_next_link_from_resp` function is called while iterating through responses to reach the desired number of entities. This effectively allows a given model to iterate through pagination. Its input is a `requests.Response` object and by default this function looks for the `links` object's `next` value. You can choose to override it however you want, but you must return either a string value matching the next URL to request to, or a false value (none or False ideally) if there isn't another page to iterate through.

### get_meta_data_from_resp(self, request_resp) -> `dict`

This function takes a response object and generates the meta data that a MagellanResponse returns as a part of the `get_meta_data()` function. By default it returns a dict with keys `meta` and `links` corresponding to the same keys in the response JSON body.
