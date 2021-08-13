# Querying and Attributes

A key focus of Magellan is providing the ability to seamlessly query resources on the backend API. Querying can be done through many different ways, and we'll cover the main ways here.

For the purposes of this documentation, we will have the following set up in place. The resource in question will be `/factions` and we will have a `Faction` model. Additionally the `/factions` entities include a parsed set of relationships to `units` and `universe` where there's a singular universe and many units for any given Faction entity. Universes and Units also have their own models under Magellan's returned models dict. We are also assuming the user configuration works properly in these examples below.


## Querying a single resource

There are many ways to query a singlular resource by the main ways are via `find` and `find_by_{attribute}`.

### Find()

If I have an ID value that I want to use to search for a resource I can make a GET request to the `factions/ID` route. If the backend has a resource with that ID, it'll return that resource, and if it doesn't I'll get a 404 response. We can make calls to that endpoint using the `find(id)` function which returns a singular Magellan Model instance or an exception if we can't find a value or there's any other server error encountered.

```python
inst = Faction.find("6eaac923-6a1f-4555-8c3f-afa3b9974675")
inst.id # => "6eaac923-6a1f-4555-8c3f-afa3b9974675"
inst.title # => "The Empire"
```

Here we are looking for a faction with the ID "6eaac923-6a1f-4555-8c3f-afa3b9974675". We use the `.find()` function to look for that ID value, and in the end we get back a result.

### find_by_{attribute}

Additionally, say we wanted to search for the first faction with a title, or some other identifier (say a description value). In this case, if that attribute is present in the OpenAPI specification, we can utilize a helper function that will query the `/factions` endpoint with a filter for that attribute. If we get any results back we'll return the first element we receive. This is important because if we receive multiple elements back in the response, only the first is returned to the user.

```python
inst = Faction.find_by_title("The Hive")
# This call does a GET /factions with a filter for the title, and a limit of 1
inst.id # => "6eaac923-6a1f-4555-8c3f-afa3b9974675"
```

What's noteworthy is that these find_by functions will still provide the opportunity to provide your own attribute_operation (if your config supports it) and header arguments.

## Querying for many results

If you wish to get aggregate collections of a resource, you can use the `where` and `query` functions to get a list of results back. For most users, the `where` function is probably the most useful.

### `where(limit=None, **kwargs)`

`where` is the primary means of querying the API. You can pass assignment operations for any set of attributes available to the model, and then a limit value (defaults to None for limit-less). `where` is useful if you want to search for all results in a list of possible IDs, or search for all elements with a similar title.

```python
# Search for Factions in a list of IDs
ids = ["123", "124", "125"..., "130"]
list_of_factions = Faction.where(id=ids, filtering_arguments={"id": "in"}) 
# search for all factions where the ID is in the list of IDs

matching_creator = Faction.where(creator_id="10938fk3910230", limit=10) 
# => a list of up to 10 factions whose creator ID matches the input ID, remove the limit argument to find all factions

compound_list = Faction.where(creator_id= my_id, id= ids, created= myTimestamp, filtering_arguments={"id": "in", "created": "geq"}, limit=100) 
#=> Find the first 100 entities created by Me, with an ID contained in the ids list, and created after or at a point in time past myTimestamp
```

the `where` function provides most of the utility available in the `query` function but its abstractions may make certain queries more difficult.

### `query(parameters={}, limit=None, **kwargs)`

The Query method takes in a list of parameters (that are preformated by the user) and sends a get request using the page number and per page values supplied. Query if useful if you already have the parameters you want. However due to it requiring you to define the parameters manually, it removes a lot of the "magical abstraction" that magellan tries to do for you. By default query will go through all the pages available for a given result. You can limit this by setting the `limit` value to a non-negative integer.

### Chaining with `where`

The `where` query supports method chaining as well. This lets you create compound filters using multiple API calls. What's important to note is that first, the API will get accessed at least once per chained `where` call, and second, the chained `where` call will also reset the internal state of a given response.

```python

results = Faction.where(creator_id = my_id).where(tag=my_tag)
# Get all results created by me with a specific tag

# To set a limit after the first `where` call: 
results.limit(10) # Limits the number of results. This also is destructive to the internal state
```

You can also pass filtering_arguments in each `where` call as well.

### The MagellanResponse object

Both the `where` and `query` functions return a `MagellanResponse` object which acts as an iterable. The `MagellanResponse` is designed to allow for non-application-stalling API access when handling large amounts of results from an API. For example, a query to return all entities generated after 1971 might lead to a lot of results. Instead of iterating through each page of results from the API and parsing the results into Magellan models, the `MagellanResponse` will only fetch a page when the current elements have already been processed.

The `MagellanResponse` object has the following user friendly (external facing) functions:

#### `iteration_is_complete() -> bool`

This function returns whether or not the MagellanResponse has fully found all results it expects. Effectively either its consumed up to its limit, or it doesn't have another page of results to fetch.

#### `evaluate_fully() -> None`

This function will iterate through each page of results until iteration is complete. This can cause the application to stall if there are too many results.

#### `get_meta_data -> dict`

Returns the meta data (the structure of which is defined via the configuration object) for this MagellanResponse.
