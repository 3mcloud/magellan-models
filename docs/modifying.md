# Modifying Resources via POST, PATCH, and DELETE

While reading resources is probably the main way most people will ever use Magellan, there's also the ability to modify resources "back home" in the backend. This can be done via posting your own model instances to the backend or patching a modified instance that was initialized via a query to the backend. You can also choose to send a delete request if your backend supports DELETE requests.

## POSTing

You can POST to the backend using two different methods, the class method `post_payload()` and the instance method `post`. The instance method is useful if you want to directly POST the model instance's representation to the backend API. 

```python
inst = Sample() 

# modify and set the instance's attributes
...

inst.post() # send a post request with the models attributes in the request body

inst.id # => should now be set to an ID returned from the backend
```

When you use the `post()` method, the server response json will be used to redefine the attributes of whatever instance was posted. This means fields like ID and relationships will be reset to whatever the server returned.

To post using any arbitrary JSON payload you can call the `post_payload()` function. This function takes in an arbitrary json payload, and then converts the JSON response from the POST request into a MagellanModel instance.

```python
inst = Sample.post_payload(myJsonDict)

inst.id # => a server assigned UUID 
inst.title # => "Hello from Magellan's Post Payload!"
```

Under the hood, the `post()` method actually calls the `post_payload()` function, so often times you'll see issues arise regardless of which method you use if your json or your instance representation is malformed.


## PATCHing

Say you already had a Magellan model instance and wanted to update it on the backend? You can modify the attributes of the model instance and then send a `patch()` call to update the backend with your changes. The `patch()` function takes the instance's representation and converts it into a PATCH request to the `/resource/id` path.

```python
instance = Sample.find_by_title("Before the PATCH")
instance.title = "Patched via Magellan"
instance.patch() # => sends a PATCH request with the updated Title
instance.title # => "Patched via Magellan" on the backend and Magellan Instance
```

## DELETE-ing

Well what if you wanted to delete a resource that's stored in the backend? Here you have two options, the class method `delete(id)` and the instance method `delete_self()`. In order to delete a resource, just pass the ID of the entity you want to delete and it'll send a DELETE request. Just note that this won't remove the Magellan model instance from your environment. You'll need to discard it on your own. 

```python
# Both of these calls send the same DELETE request to /samples/123
Sample.delete(123)
Sample.find(123).delete_self()
```

### Sync 

Actions like PATCH and POST along with changes to local instances while other people are modifying resources can often cause a Magellan model to become out of synchronization with the backend API. To combat this a `sync()` function is available to instances which will "refresh" the data representation, discarding all local variation between the instance and it's backend resource value. 

```python
inst.sync() # Refresh the instance with the latest data on the backend
```