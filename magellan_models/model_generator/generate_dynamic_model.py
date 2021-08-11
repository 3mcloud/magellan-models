"""
    Module that generates the Magellan model when given all the information it needs
"""
import re
from copy import deepcopy
from typing import Callable
import inflection
from magellan_models.interface.abstract_api_model import AbstractApiModel
from magellan_models.config import MagellanConfig
from magellan_models.exceptions import MagellanRuntimeException
from magellan_models.model_generator.generate_nonrest_functions import (
    generate_func_for_route,
)


def exception_function(*args, **kwargs):
    """Function that raises a MagellanRuntimeException

    Invoked when the function is part of the disabled_functions iterable in the magellan config
    """
    raise MagellanRuntimeException("This function has been disabled!")


def generate_model(  # pylint: disable=dangerous-default-value,too-many-statements,too-many-locals
    model_representation: dict,
    all_model_names: list,
    model_mapping: dict,
    configuration: MagellanConfig,
) -> Callable:
    """
    Generates a Model Class dynamically when given a model_representation dict,
    a list of all_model_names, and the currently mapped models
    This Dict need to have the following:
    'resource_name' : str
    'class_name' : str
    'attributes' : dict[str => type]
    'relationships' : dict[str (name) => str (one of many ; one)]
    'downstream_routes' : List
    'patch_req_schema': dict
    'post_req_schema': dict

    The all_model_names list is composed of strings for each model's class name.
    This is used to detect which relationships need model helper methods and which don't.

    The currently mapped models is a dictionary of model_name => Model object definition.
    This is used for the relationship generator to have access to the model.
    It's assumed that upon completion of all generation events,
    that the model_mapping will have an entry for each entity in all_model_names

    configuration is a user defined MagellanConfig instance
    """

    # deep copy mutable data structures, just assign local variables for immutable values
    # lets me try to avoid issues where we call generate_model multiple times in a runthrough
    # because that'll be a pain to troubleshoot

    attributes = deepcopy(model_representation.get("attributes", {}))
    relationships = deepcopy(model_representation.get("relationships", {}))
    downstream_routes = deepcopy(model_representation.get("downstream_routes", []))
    class_name_val = model_representation["class_name"]
    resource_name_val = model_representation["resource_name"]
    post_schema = deepcopy(model_representation.get("post_req_schema", {}))
    patch_schema = deepcopy(model_representation.get("patch_req_schema", {}))

    def list_attributes_function():
        attributes_response = {}
        for attribute in attributes:
            # case type to string
            attributes_response[attribute] = attributes[attribute].__name__
        return attributes_response

    def post_schema_wrapper_func():
        return post_schema

    def patch_schema_wrapper_func():
        return patch_schema

    def list_functions_func():
        return list(mapping.keys())

    def init_function(self):
        relationship_body = {}
        for relationship in relationships:
            relationship_name = (
                inflection.pluralize(relationship)
                if relationships[relationship] == "many"
                else relationship
            )
            relationship_value = [] if relationships[relationship] == "many" else {}
            relationship_body[relationship_name] = {"data": relationship_value}
        self.__dict__["__representation"] = {
            "attributes": {},
            "relationships": relationship_body,
        }

    def resource_name_func():
        "returns the resource name we have passed in"
        return resource_name_val

    def representation(self):
        return self.__representation  # pylint: disable=protected-access

    def process_get_attributes(self, method_name):
        if method_name in attributes:
            return self.get_instance_attribute(method_name)
        raise AttributeError(f"No such attribute: {method_name}")

    def process_set_attributes(self, attrib_name, attrib_value):
        if attrib_name == "__representation":
            # todo: find a better way to handle this
            self.__dict__["__representation"] = attrib_value
        elif attrib_name in attributes:
            self.set_instance_attribute(attrib_name, attrib_value)
        elif attrib_name == "representation":
            setattr(self, "__representation", attrib_value)
        else:
            raise AttributeError(f"No Such attribute: {attrib_name}")

    mapping = {}

    ### Attributes logic ###
    for attribute in attributes:
        find_by_func_name = f"find_by_{attribute}"

        def find_by_func(cls, value, operation="eq", bound_attrib=attribute, **kwargs):
            entity = cls.where(
                **{
                    bound_attrib: value,
                    "filtering_arguments": {bound_attrib: operation},
                },
                limit=1,
                **kwargs,
            )
            if len(entity) == 1:
                return entity[0]
            return None

        mapping[find_by_func_name] = classmethod(find_by_func)
    ### end attributes logic###

    ### Relationships logic ###
    relationship_function_names = []
    for relationship_name in relationships:
        json_name = f"{relationship_name}_json"
        mapping[
            json_name
        ] = lambda self, relationship_name=relationship_name: self.get_instance_relationship_value(
            relationship_name
        ).get(
            "data"
        )
        relationship_function_names.append(json_name)

        if relationships[relationship_name] == "many":
            singular_name = inflection.singularize(relationship_name)
            add_name = f"add_{singular_name}"

            def add_relationship_func(
                self,
                added_elem_id,
                additional_args={},
                relationship_name=relationship_name,
                singular_name=singular_name,
            ):
                """Adds a given UUID to the relationship body of a given instance of a resource"""
                current_entities = self.get_instance_relationship_value(
                    relationship_name
                ).get("data", [])
                current_entities.append(
                    configuration.relationship_id_to_json_entry(
                        added_elem_id,
                        relationship_type=singular_name,
                        additional_args=additional_args,
                    )
                )
                self.set_instance_relationship_value(
                    relationship_name, {"data": current_entities}
                )

            remove_name = f"remove_{singular_name}"

            def remove_relationship_func(
                self,
                removed_elem_id,
                relationship_name=relationship_name,
                singular_name=singular_name,
            ):
                """Removes a given UUID from the relationships body"""
                current_entities = self.get_instance_relationship_value(
                    relationship_name
                )
                current_entities = current_entities.get("data", current_entities)
                if current_entities is None:
                    current_entities = []
                mapped_entity = configuration.relationship_id_to_json_entry(
                    removed_elem_id, relationship_type=singular_name
                )
                if mapped_entity in current_entities:
                    current_entities.remove(mapped_entity)
                    self.set_instance_relationship_value(
                        relationship_name, {"data": current_entities}
                    )

            if (
                inflection.camelize(inflection.singularize(relationship_name))
                in all_model_names
            ):

                helper_get_name = f"{relationship_name}"

                def helper_get(self, _relationship_name=relationship_name, **kwargs):
                    """
                    Helper method that returns Instance models for each {{relationship}}
                    currently linked to this instance
                    """
                    filtering_arguments = kwargs.pop("filtering_arguments", {})
                    filtering_arguments["id"] = "in"
                    ids = [
                        relationship["id"]
                        for relationship in self.get_instance_relationship_value(
                            _relationship_name
                        ).get("data")
                    ]
                    relationship_model_name = inflection.camelize(
                        inflection.singularize(_relationship_name)
                    )
                    entities = model_mapping[relationship_model_name].where(
                        id=ids,
                        filtering_arguments=filtering_arguments,
                        limit=len(ids),
                        **kwargs,
                    )
                    return entities

                mapping[helper_get_name] = helper_get
                relationship_function_names.append(helper_get_name)

            mapping[add_name] = add_relationship_func
            mapping[remove_name] = remove_relationship_func
            relationship_function_names.append(add_name)
            relationship_function_names.append(remove_name)
        else:
            # do set_relationship_id and set_relationship alongside the get_relationship
            # if its in the model names list
            set_id_name = f"set_{relationship_name}_id"

            def set_id_func(
                self, new_id, additional_args={}, relationship_name=relationship_name
            ):
                relationship_entity = configuration.relationship_id_to_json_entry(
                    new_id,
                    additional_args=additional_args,
                    relationship_type=relationship_name,
                )
                self.set_instance_relationship_value(
                    relationship_name, {"data": relationship_entity}
                )

            set_name = f"set_{relationship_name}"

            def set_func(
                self, new_entity, meta={}, relationship_name=relationship_name
            ):
                relationship_entity = configuration.relationship_id_to_json_entry(
                    new_entity.id, meta=meta, relationship_type=relationship_name
                )
                self.set_instance_relationship_value(
                    relationship_name, {"data": relationship_entity}
                )

            if inflection.camelize(relationship_name) in all_model_names:
                # helper get
                get_name = f"{relationship_name}"

                def get_func(self, relationship_name=relationship_name):
                    relation_id = (
                        self.get_instance_relationship_value(relationship_name)
                        .get("data")
                        .get("id", None)
                    )
                    if relation_id is None:
                        return None
                    return model_mapping[inflection.camelize(relationship_name)].find(
                        relation_id
                    )

                mapping[get_name] = get_func
                relationship_function_names.append(get_name)

            mapping[set_id_name] = set_id_func
            mapping[set_name] = set_func
            relationship_function_names.append(set_id_name)
            relationship_function_names.append(set_name)

    def list_relationships_wrapper(
        func_names: list = relationship_function_names,
    ) -> list:
        return func_names

    ### end relationships logic###

    ### Downstream Route logic ###
    downstream_name_list = []
    for route in downstream_routes:
        action = route["action"]
        # get the first element of the short path
        short_path = route["short_path"].split("/")[0]
        func_name = f"downstream_{action}_{short_path}"
        downstream_name_list.append(func_name)

        # get the function NOT the string name
        downstream_func = generate_func_for_route(route, configuration)[1]

        # need to parse out ID separator in use for this route...
        full_path = route["route"]
        id_sep = re.compile(configuration.id_separator)
        separator = re.search(id_sep, full_path).group(0)
        parsed_id_key = re.match("{(.*)}", separator).group(1)

        # Need to keep route_obj to maintain unique function declaraction
        def wrapper_func(  # pylint: disable=unused-argument
            self,
            id_label=parsed_id_key,
            route_obj=route,
            passed_func=downstream_func,
            **kwargs,
        ):
            # Pass in self.id to the downstream function
            return passed_func(**{id_label: self.id}, **kwargs)

        mapping[func_name] = wrapper_func

    def list_downstream_wrapper(func_names: list = downstream_name_list) -> list:
        return func_names

    ### end downstream route logic ###

    mapping["resource_name"] = staticmethod(resource_name_func)
    # getter function for the passed in configuration
    mapping["configuration"] = classmethod(lambda cls: configuration)
    mapping["__getattr__"] = process_get_attributes
    mapping["__setattr__"] = process_set_attributes
    mapping["list_attributes"] = staticmethod(list_attributes_function)
    mapping["representation"] = property(representation)
    mapping["__init__"] = init_function
    mapping["list_methods"] = staticmethod(list_functions_func)
    mapping["id"] = property(lambda self: self.get_instance_attribute("id"))
    mapping["get_post_schema"] = staticmethod(post_schema_wrapper_func)
    mapping["get_patch_schema"] = staticmethod(patch_schema_wrapper_func)
    mapping["list_downstream_functions"] = staticmethod(list_downstream_wrapper)
    mapping["list_relationship_functions"] = staticmethod(list_relationships_wrapper)

    ### Handle disabling functions
    for func_name in configuration.disabled_functions:
        mapping[func_name] = exception_function

    Model = type(  # pylint: disable=invalid-name
        class_name_val, (AbstractApiModel,), mapping
    )
    return Model
