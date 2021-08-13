[![CI](https://github.com/3mcloud/magellan-models/actions/workflows/gh_actions.yml/badge.svg)](https://github.com/3mcloud/magellan-models/actions/workflows/gh_actions.yml)

# Magellan-Models

Dynamically Generate client-side models for interfacing with your own OpenAPI 3.0 compliant JSON API endpoints.

![Magellan Models Moose](./docs/images/originalImageViaRyanHagerty2021.png)

## What is it?

Magellan Models (referred to as Magellan throughout the rest of this documentation) is a code generator that generates "client-side models" for a given OpenAPI spec that follows (by default) the JSON:API specification. A developer can modify their own configuration to provide support for other API specifications so long as they can also provide their own OpenAPI 3.0 json specification.

### How does Magellan compare to other OpenAPI client libraries like pyswagger, swagger-codegen, or bravado?

Magellan prides itself in having an easier time to set up and get running. Most other OpenAPI client libraries require setting up authorization and importing custom clients and the result is a verbose and clunky syntax. Magellan instead tries to parse responses back for the user to ensure that accessing and modifying response elements is a seamless task. Alternative libraries often tend to differentiate between the client which sends requests and receives responses and the model itself which is a representation of data. Magellan however treats them both as the same, leading to less mental overhead for the developer (when things work).

Magellan however will require some more setup in the configuration, often requiring you to override parts of the configuration you don't want to keep. The other libraries will let you do so in a more pythonic way at runtime without resorting to creating a new magellanConfig inheriting class defintion.

### How does Magellan compare to other JSON:API consumer libraries like [json-api-smart](https://github.com/NilssonPL/json-api-smart)?

Oh wow, that looks really similar to what Magellan does! You even query the backend in almost the exact same way! If you're willing to document out your API manually as a part of your project, then you'll probably have better luck with a package like json-api-smart. The allure of Magellan in this instance is that Magellan will autogenerate models for you to use via the OpenAPI specification file, while other JSON:API clients tend to require you to define your endpoint and your models and attributes manually. Magellan will try to parse out attributes for you, assign types, and further create helper methods for relationships (including matching relationships to models if it can find a direct match).

As a user, it's up to you to decide if the automated functionality (and less present documentation) that Magellan provides is sufficient for your use case, or if you'd prefer a more "typed" out experience that other client libraries tend to offer.

## Installation

`pip install git+ssh://git@github.com/3mcloud/magellan-models.git` will install the latest "master" branch version of Magellan.


## Potential workflow

```python
    from magellan_models.initializers import initialize_with_endpoint
    from magellan_models.config import MagellanConfig
    from my_json_file import myJsonSpec

    ... 

    conf = MagellanConfig() 

    # Modify Configuration settings inside of the config object
    conf.api_endpoint = "https://myAPIurl" 

    # Now Generate a tuple of models, functions, and a configuration object via the initialization function
    (models, funcs, config) = initialize_with_json(open_api_spec=myJsonSpec, model_config= conf)

    ... 

    # Pull a model out of the models dictionary
    ModelResource = models["ModelResource"]

    # Here we are doing a GET request to "/model_resources/uuid_str_id_variable" and parse the response into a Magellan "Model" instance
    instance = ModelResource.find(uuid_str_id_variable)

    # You can then access response attributes as model attributes for a given instance
    print(f"{instance.title}: created at: {instance.created}, modified at: {instance.modified}")
    
    ... 
    
    # Alternatively use the "where" method to search for collections with your own filtering options
    
    ElectronicComponent = models["ElectronicComponent"]
    
    # The config will dictate how we parse these arguments and format them into a filter
    # It could be as simple as filter[lotNum]="myLotNum"&filter["creator_id"=my_creator_id
    # or more complex like filters=[{field: "lotNum", val: "myLotNum", op: "eq"}, {field: "creator_id", val: my_creator_id, op: "eq"}]
    # It all depends on how you define your Magellan config!
    components = ElectronicComponent.where(lotNum="myLotNum", creator_id= my_creator_id) # Returns a MagellanResponse which handles pagination to prevent large stalling periods
    for component in components: 
        # Let's print the title out as we iterate through our results!
        print(component.title)

```

## Model features

* CRUD route functionality baked in with functions for POST, PATCH, DELETE, and GET
* Automatic response parsing from GET calls to return either a singular Model instance or a List of Model instances
* Attributes from the response are set up as "native" attributes for a given model (given {"data": {"attributes": {"title": "foo"}}} a model will know that instance.title refers to "foo")
* Filtering operations are built to map an easy to use developer interface to whatever filtering strategy employed by the API
* Proper serialization into a format that can be PATCH/POSTed to the endpoint url
* Relationships data is parsed and helper functions are provided to access relationship entities

## Overview Docs

For specific documentation that's more in depth on each of the various facets of Magellan, check out the specific documentation pages!

* [The MagellanConfig class and setup](./docs/configuration.md)
* [The initializer functions](./docs/initialization.md)
* [Querying the backend API](./docs/querying.md)
* [Model Attributes and relationships (reading and writing)](./docs/model_attributes.md)
* [Modifying via POST and PATCH to the backend API](./docs/modifying.md)
* [Notes about the Model Representation Object](./docs/representation.md)
* [Information about the functions generated by Magellan](./docs/generated_functions.md)

### Configuration setting

Each initialization requires a passed in MagellanConfig entity. If you want to override any functionality or specify your API url, you'll want to modify the configuration instance that you've passed in. These modifications can also be done after initialization! Say your token is stored in a configuration instance and expires, you can choose to override your token value with a new one during runtime while not interrupting any of your models' functionality! See the `configuration.md` file in the Docs for more information about MagellanConfig.

### Getting entities

All entities are returned via class methods. The main ones you'll want to use are `where()` and `query()`. For most use cases, `where()` will probably be sufficient but `query()` is designed with more complex querying in mind.

#### `where()`

`where()` takes in any number of arguments where the argument name corresponds to the attribute you want to filter on. For example, `where(lotNum="blah")` sets a filter for `lotNum` to be equal to `blah`. `where()` also has a "limit" key which defaults to None and defines how many results to return (by default finding all available results).

`where()`also takes in a "filtering_arguments" argument which is a dictionary. This dictionary has the arguments passed in as keys, and has the filtering operation as the return value. These filtering operations default to "eq" if not specified but can be values such as "in" or "ilike" etc.

Passing in a "sort" argument also lets you order elements in the backend as well.

example:
` ElectronicComponent.where(lotNum=["blah", "foo", "bar"], creator_id= steves_id, attribute_mapping={"lotNum": "in"}, limit=100) `

This call searches for the first 100 Electronic Components created by Steve where the lotNum is either "blah", "bar", or "foo"

#### `query()`

This method is currently somewhat functional. It takes in a list of filters, a page_number value, and per_page value, and returns the results as model instances.

Filters are dictionaries with "key", "op", "val" keys.

Example:
`ElectronicComponent.query(parameters={"filters": [{"key": "title", "op": "eq", "val": "Example Title" }], "page_number": 1, "per_page"=30}, limit=30 )`
Returns all the entities returned from a single GET call with 30 results max, in the first page of the pagination results, where the "Title" equals "Example Title"

#### Singular Queries

What if you wanted to get a single item by a "title" field or "id"? The easiest way is to use the `find(id)` method, which submits a GET request to the `https://api/model_resource/ID` route. If that ID exists, you'll get a model instance back, and if it 404s, you'll get None returned.

` ElectronicComponent.find("a valid UUID") -> instance(ElectronicComponent) `
` ElectronicComponent.find("invalid ID") -> None `

If you wanted to find a single entity by a given attribute, you can also do that using the `find_by_{attribute}` helper methods. These methods return THE FIRST entity that matches a given attribute.

Example:
`ElectronicComponent.find_by_lotNum("a valid lotNumb") -> instance(ElectronicComponent)`

### Modifying Entities

#### Attributes

As part of the schema parsing steps when initializing the models, Magellan will go through the response and request bodies and parse out a set of attributes. These attributes will then be converted into instance properties for each class.

To get a list of Attributes, the static method `list_attributes()` will return the possible attributes parsed from the specification.

For example, say a resource "/users" returns entities with the attributes "first_name", "last_name", "id", and "email". The `User` model corresponding to this resource will have defined attributes corresponding to each of those 4 that the server states it accepts and receives.

example:

```python
    user = User()
    user.first_name = "Tycho"
    user.last_name = "Brahe"
    user.email = "iwantmynoseback@spacemail.com
    print(user.first_name + " " + user.last_name) # -> Tycho Brahe
```

If you're getting a model instance back from the server (say via the `find()` method), these attributes will be prepopulated with the server response.

example:

```python
    user = User.find_by_id(tycho_id)
    print(user.first_name) # -> Tycho
```

#### Relationships

Relationships are also parsed from the OpenAPI schema. There are two cases that each relationship can fall into: singular (there's a single entity like "experiment" or "user" being returned), or plural (there's an array of entities being returned (like "experiments"). **Differentiation is done via the pluralization of the relationship key**. If the relationship key is a singular value, it will be treated as a singular relationship. Eventually this will be updated, but at the moment, it functions of key pluralization rather than the specification itself. You can call `list_relationship_functions()` to get a list of possible relationship modification functions.

##### Singular Relationships

For singular relationships, you can retrieve the relationship object's ID through the `{relationship}()` method. You can also call the `set_{relationship}_id(id)` method to set the relationship object via its id. You can also call `set_{relationship}( relationship_instance)` to update the relationship using an object instance that you want to couple (rather than passing the object's ID in).

##### Plural Relationships

Plural relationships expect a list of relationship object IDs. instead of having the `set_{relationship}_id(id)` method, you'll instead be able to use `add_{relationship}(id)` and `remove_{relationship}(id)` methods which modify that list of relationship IDs for a given model instance.

You can also call the `{relationship}()` method which converts each of those ID entities into an object instance to manipulate **if the relationship name maps to a generated Class** or `{relationship}_json()` which returns the raw json for the relationship body.

```python
# Example of plural relationships;
# If a given ElectronicComponent has many Tests
component = ElectronicComponent.find(123)
component.tests() #-> [Test1<>, Test2<>, Test3<>, ...] 
component.add_test(test_four_id) 
component.remove_test(test_two_id) 
component.tests() #-> [Test1<>, Test3<>, Test4<>...]
```

### Creating and Updating Entities

#### `post()`

To create an entity on the backend, you can call the `post()` method. This sends a POST request to the `/{resource}` path. A successful post should then also generate an ID for the instance and updates the instance with the server response attributes (oftentimes useful for updating the timestamps of a given class instance).

#### `patch()`

Patching is used for class instances that have an ID associated with them on the backend. calling `patch()` sends a PATCH request to the `/{resource}/{instance_id}` path. The class instance is then updated with the server response after the PATCH request.

### Deletions

`delete_self()` can be used to send a delete request. Try to avoid using this too often since the data then becomes lost. `delete_self()` only works for entities that have been created on the API end, and for entities that have an ID as a result.

## Contributing

1. Create a new branch from Master
2. Make changes in your new branch
3. Open a Pull Request and request approval from any of the contributors of the code base (most likely talha-ahsan)
4. Upon approval it'll be merged into master, if this PR should be its own standalone "release" it'll then be released at that time.
