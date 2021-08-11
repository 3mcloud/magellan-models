# Magellan generated Functions

When you call an initializer function, you'll get back the models, functions, and a configuration instance linked to those models and functions. While the models provide a higher level of abstraction when interfacing with an API, the functions generated act more as wrappers around specific paths that the API makes available. Often these paths don't have a clear home in any given generated model.

An example of a commonly generated function is the function for calling the GET /healthcheck route.

```python
models, funcs, config = initialize_with_json(myJson, myConf)
funcs.keys() # => ["get_from_healthcheck", "post_to_upload", ...]
resp = get_from_healthcheck()
res.json() # => {"status": 200, "message": "Hello World. All is well"}
```

These functions are thin wrappers around the actual API route. They handle the following:

* Parameter names are pulled and can be substituted by passing the value in as a keyworded argument
* Header generation is handled using the MagellanConfig defined header generation function
* Default arguments to pass to the `requests` package are injected at the point of sending the HTTP request

This lets the user do something like the following:

```python
models, funcs, config = initialize_with_json(myJson, myConf)
resp = post_to_echo_with_message(message="Hello World") # hits POST /echo/{message} with "Hello World" subbed in
resp.json() # => {"message": "Hello World"}
```

If you wanted to pass in a body, the `request_body` kwarg is available and defaults to `{}`. This leads to the function declaration being as such for the user: `my_functional_wrapper(request_body={}, **kwargs)` where any parameters in the path can be passed in as kwargs. Note the actual function declaration is a little different in order to ensure functionality. Additional arguments that have default values for each wrapper function should not be tampered with or you'll risk breaking the wrapper on invocation.