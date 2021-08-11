# The Model Instance Representation Object

A common stumbling block is not understanding the various decisions made around the model's representation object.

This object _is_ opinionated to an extent and requires users to map data from their API into the representation format.

The representation object is effectively a dictionary that has a few rules:

1. There needs to be a distinct path to the `attributes` for a given instance.
2. There needs to be a distinct path to the `relationships` for a given instance.

It's possible for those paths to be identical but it opens up a lot of space for bugs and unintended side effects to manifest.

## The Attributes

Attributes are stored in the representation's `attributes` object as a standard key value pair. You can define the path to this attributes object via the configuration settings. This means you can in theory nest the attributes further down in the representation in case your API wants you to have data be nested x layers deep. Check out the `configuration.md` documentation to learn more about the path variables.

## Relationships

Relationships are where things get a little messier. By default a relationship ID is represented by the following object:

```json
{
    "type": "object",
    "properties": {
        "id": {
            "type": "string || numeric"
        },
        "type": {
            "type": "string"
        }
    }
    
}

// Example: 
{
    "id": "myexampleId",
    "type": "relationship name"

}
```

Additionally that object is retrievable through the `"data"` key which yields a single object of the above schema for a singular relationship or an array of the above objects for a "many" relationship.

```json
// An example of how this relationships schema works out in practice
{
    "relationships": {
        "my_first_relationship": {
            "data": {
                "id": "singular id",
                "type": "my_first_relationship_type"
            }
        },
        "a_many_to_many_relationship": {
            "data": [
                {"id": 1, "type": "foo"},
                {"id": 2, "type": "foo"},
                ...
                {"id": n, "type": "foo"}
            ]
        }
    }
}
```

When converting relationships to and from a server response, make sure you're doing your best to maintain this schema. At the moment, Magellan's model relationship helper heavily operates under this assumption that the relationships are structured in this way. The good news is that if your API follows json:api conventions, then there's very little conversion necessary from the client side to get Magellan up and running!