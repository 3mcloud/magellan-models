# Experimental Features

Some features may be marked as "Experimental" indicating that they're not final, prone to being buggy or incomplete, and very unlikely to add meaningful functionality to the user.

To enable experimental features, set the `experimental_functions` attribute for your configuration to `True` instead of `False`. 

## Current Experimental Features:

The MagellanResponse object can have filtering and sorting functions generated with the following regex matching: 

`filter_by_{attribute}(value: any, filtering_arg: str (default "eq"))`

Example: `Faction.where(creator_id="me").filter_by_title("Foo")`

`filter_{attribute}__{filtering_arg}(val)`

Example: `Faction.where(creator_id= "me").filter_title__eq("foo")`
Note the double underscore between `title` and `eq`. This is a stopgap measure to handle instances where both the operation or the attribute may have underscores in them

`sort_by_{attribute}`:

Example: `Faction.where().sort_by_title()`

Each of these current features wrap around the `where` chaining function to allow for testability and predictable results.
