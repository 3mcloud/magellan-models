# Model Attributes and Relationships

Once we've retrieved a model instance from our backend, we probably will want to view or modify some of the attributes or relationships that model has. This section covers reading and modifying attributes and relationships.

To get a list of Attributes, the static method `list_attributes()` will return the possible attributes parsed from the specification. To get a list of Relationships, the static method `list_relationship_functions()` returns the possible functions you can call for a given Model instance. Lastly to get a list of downstream route helper functions, you can call `list_downstream_functions()` to have those be printed out.

Additionally you can use the static method 'list_methods()' which returns the list of all methods available for a given model.

## Attributes

Say we have a `Faction` model instance named `faction_instance`. Additionally, the OpenAPI specification lists that there are 4 attributes `id, title, description, meta` for a given faction instance. We can directly query the attributes for an instance using the following syntax:

```python
faction_instance.id #=> returns the ID attribute
faction_instance.title #=> returns the Title attribute
faction_instance.nonAttribute # raises an AttributeNotFound error
```

Effectively the Magellan model generator will create property definitions for each attribute allowing for easy lookup and reference. Say we wanted to modify the attribute `title` in the instance, since the attribute is a property we can use the same basic attribute setter syntax to modify our instance!

```python
faction_instance.title = "new Title" 
assert faction_instance.title == "New Title" # passes 
```

It's important to note that these attributes are only a single layer deep, meaning if you have a dict object as an attribute, you'll need to set the whole dict and won't have helpful syntax to traverse the dict by itself.

```python
faction_instance.meta.innerLayer.attrib = "fudge" # this doesn't work!
faction_instance.meta["innerLayer"]["attrib"] = "fudge" # this should work
```

Attribute access can be further configured in the MagellanConfig file.

## Relationships

Relationships are also parsed from the OpenAPI schema. There are two cases that each relationship can fall into: singular (there's a single entity like "experiment" or "user" being returned), or plural (there's an array of entities being returned (like "experiments"). **Differentiation is done via the pluralization of the relationship key**. If the relationship key is a singular value, it will be treated as a singular relationship. Eventually this will be updated, but at the moment, it functions of key pluralization rather than the specification itself.

For any relationship you can call `{relationship_name}_json()` to get the raw dictionary object storing relationship data for a relationship. This tends to be either a dict, or a List of dicts.

##### Singular Relationships 

For singular relationships, you can retrieve the relationship object's ID through the `{relationship}()` method. You can also call the `set_{relationship}_id(id)` method to set the relationship object via its id. You can also call `set_{relationship}( relationship_instance)` to update the relationship using an object instance that you want to couple (rather than passing the object's ID in).

##### Plural Relationships

Plural relationships expect a list of relationship object IDs. instead of having the `set_{relationship}_id(id)` method, you'll instead be able to use `add_{relationship}(id)` and `remove_{relationship}(id)` methods which modify that list of relationship IDs for a given model instance.

You can also call the `{relationship}()` method which converts each of those ID entities into an object instance to manipulate **if the relationship name maps to a generated Class** or `{relationship}_json()` which returns the raw json for the relationship body.

```python
# Example of plural relationships;
# If a given Faction has many units
faction_instance.units() #-> [<Unit1>, <Unit2>, <Unit3>, ...]
faction_instance.add_unit(unit_four_id) 
faction_instance.remove_unit(unit_two_id) 
faction_instance.units() #-> [<Unit1>, <Unit3>, <Unit4>,...]
```

Remember that after modifying relationships that you'll need to send a PATCH request to ensure your changes are persisted in the backend.

Additionally, you can do filtering inside the `{relatationship}()` method as well just as if you were doing a `{relationship_model}.where()` query. The arguments are the same and you can pass in attribute operations as needed. 

```python
# Example of using relationship filtering using a Faction with many units
faction_inst.units(title="Clone Trooper Squad #", filtering_arguments={"title": "starts_with"})
# The above call sends a requests filtering to check that the units returned match one of the IDs in the faction_inst units relationship attribute
# AND that the unit's title starts with "Clone Trooper Squad #"
# These filters are both applied with an "AND" operation by default, but it's up to the user to provide their own filter generator function
```

Some relationships might store more information than just the ID for a relationship entity. In order to capture this data, when setting or adding the relationship value, you can pass this information as part of the `additional_args` argument. This then is transformed as needed by the configuration's transformation functions. 

```python

faction_inst.add_unit(unit_id, additional_args={"access_level": 5, "priority": "VERY HIGH", "request_originator": "THE PRESIDENT OF THE PLANET"})

faction_inst.units_json() # -> [{"id": unit_id, "type": "Unit", "meta": {"access_level": 5, "priority": "VERY HIGH", "request_originator": "THE PRESIDENT OF THE PLANET"}}]

```

## Downstream Routes

Say you have a "University" model which has many "Lab" instances. In order to get those Lab entities, you'll need to make a call to `/universities/{id}/labs`. This is where a downstream route can help automate your request. 

For each "downstream route", which is defined as a path that begins with `{resource_name}/{id_separator}` for a generated model, a downstream route helper function is generated that parses out any additional parameters necessary to complete the request. An example of this in action is shown below: 

```python
    resp = University.find(123).downstream_get_labs() # returns a Requests Response object similar to the non-restful functions also generated
    print(resp.json())
```

The naming convention for a downstream route is as follows: `downstream_{method (oneOf('patch', 'put', 'post', 'delete', 'get'))}_{path_portion}` where path portion is the first element of the path split by "/"s after the `{id}` element of the path. In the example above it maps to `labs`. In the case of a more complex example like `/universities/{id}/labs/{lab_id}/mission_statement` the path portion will still map to `labs` leading to a name conflict. This will be patched in a future release.
