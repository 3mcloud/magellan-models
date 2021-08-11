import os

# Move to blahblahblah.json instead of in helper.py
# Then a fixture function can call the json and return it
testing_openapi_spec = {
    "openapi": "3.0.0",
    "info": {"title": "Testing OpenAPI Spec for Magellan", "version": "1.0.0"},
    "servers": {"url": "/api/v1"},
    "paths": {
        "/healthcheck": {
            "get": {
                "summary": "GET healthcheck",
                "responses": {
                    "200": {
                        "description": "success",
                        "content": {"application/json": {"schema": {"type": "object"}}},
                    }
                },
            }
        },
        "/healthcheck/{msg_}": {
            "get": {
                "summary": "GET healthcheck",
                "parameters": [
                    {
                        "name": "msg_",
                        "description": "message",
                        "in": "path",
                        "required": "true",
                    }
                ],
                "responses": {
                    "200": {
                        "description": "success",
                        "content": {"application/json": {"schema": {"type": "object"}}},
                    }
                },
            }
        },
        "/convert_name/{name}": {
            "post": {
                "summary": "post to convert Name",
                "parameters": [
                    {
                        "name": "name",
                        "description": "name",
                        "in": "path",
                        "required": "true",
                    }
                ],
                "responses": {
                    "200": {
                        "description": "success",
                        "content": {"application/json": {"schema": {"type": "object"}}},
                    }
                },
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "conversion_method": {"type": "string"},
                                    "max_characters": {"type": "integer"},
                                    "meta_payload": {"type": "object"},
                                },
                                "required": ["conversion_method", "max_characters"],
                            }
                        }
                    }
                },
            },
            "put": {
                "summary": "PUT to convert Name",
                "parameters": [
                    {
                        "name": "name",
                        "description": "name",
                        "in": "path",
                        "required": "true",
                    }
                ],
                "responses": {
                    "200": {
                        "description": "success",
                        "content": {"application/json": {"schema": {"type": "object"}}},
                    }
                },
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "conversion_method": {"type": "string"},
                                    "max_characters": {"type": "integer"},
                                    "meta_payload": {"type": "object"},
                                },
                                "required": ["conversion_method", "max_characters"],
                            }
                        }
                    }
                },
            },
        },
        "/delete_mapping/{mapping_name}": {
            "delete": {
                "summary": "delete a mapping",
                "parameters": [
                    {
                        "name": "mapping_name",
                        "description": "arbitrary mapping name to delete",
                        "in": "path",
                        "required": "true",
                    }
                ],
                "responses": {
                    "200": {
                        "description": "success",
                        "content": {"application/json": {"schema": {"type": "object"}}},
                    }
                },
            }
        },
        "/arbitrary_patch": {
            "patch": {
                "summary": "just an arbitrary patch function to generate",
                "responses": {
                    "200": {
                        "description": "success",
                        "content": {"application/json": {"schema": {"type": "object"}}},
                    }
                },
            }
        },
        "/factions": {
            "get": {
                "summary": "GET Factions LIST",
                "tags": ["Factions"],
                "responses": {
                    "200": {
                        "description": "success",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "data": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "type": {
                                                        "type": "string",
                                                        "example": "faction",
                                                    },
                                                    "id": {
                                                        "type": "string",
                                                        "format": "uuid",
                                                        "description": "Entity UUID",
                                                        "example": "b636a2e9-889a-4da9-bd2e-c52b50b5e5e2",
                                                    },
                                                    "attributes": {
                                                        "id": {"type": "string"},
                                                        "title": {"type": "string"},
                                                        "description": {
                                                            "type": "string"
                                                        },
                                                        "keywords": {
                                                            "type": "array",
                                                            "items": {"type": "string"},
                                                        },
                                                    },
                                                    "relationships": {
                                                        "type": "object",
                                                        "properties": {
                                                            "units": {
                                                                "type": "object",
                                                                "properties": {
                                                                    "data": {
                                                                        "type": "array",
                                                                        "items": {
                                                                            "type": "object",
                                                                            "properties": {
                                                                                "type": {
                                                                                    "type": "string"
                                                                                },
                                                                                "id": {
                                                                                    "type": "string"
                                                                                },
                                                                            },
                                                                        },
                                                                    }
                                                                },
                                                            }
                                                        },
                                                    },
                                                },
                                            },
                                        }
                                    },
                                }
                            }
                        },
                    }
                },
            },
            "post": {
                "summary": "Post Factions",
                "tags": ["Factions"],
                "requestBody": {
                    "required": "true",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "data": {
                                        "type": "object",
                                        "properties": {
                                            "attributes": {
                                                "type": "object",
                                                "attributes": {
                                                    "id": {"type": "string"},
                                                    "title": {"type": "string"},
                                                    "description": {"type": "string"},
                                                    "keywords": {
                                                        "type": "array",
                                                        "items": {"type": "string"},
                                                    },
                                                },
                                                "required": ["title", "description"],
                                            },
                                            "relationships": {"type": "object"},
                                        },
                                    }
                                },
                            }
                        }
                    },
                },
                "responses": {
                    "201": {
                        "description": "success",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "data": {
                                            "type": "object",
                                            "properties": {
                                                "type": {
                                                    "type": "string",
                                                    "example": "faction",
                                                },
                                                "id": {
                                                    "type": "string",
                                                    "format": "uuid",
                                                    "description": "Entity UUID",
                                                    "example": "b636a2e9-889a-4da9-bd2e-c52b50b5e5e2",
                                                },
                                                "attributes": {
                                                    "id": {"type": "string"},
                                                    "title": {"type": "string"},
                                                    "description": {"type": "string"},
                                                    "keywords": {
                                                        "type": "array",
                                                        "items": {"type": "string"},
                                                    },
                                                },
                                                "relationships": {
                                                    "type": "object",
                                                    "properties": {
                                                        "units": {
                                                            "type": "object",
                                                            "properties": {
                                                                "data": {
                                                                    "type": "array",
                                                                    "items": {
                                                                        "type": "object",
                                                                        "properties": {
                                                                            "type": {
                                                                                "type": "string"
                                                                            },
                                                                            "id": {
                                                                                "type": "string"
                                                                            },
                                                                        },
                                                                    },
                                                                }
                                                            },
                                                        }
                                                    },
                                                },
                                                "links": {
                                                    "type": "object",
                                                    "description": "Links Object",
                                                    "properties": {
                                                        "self": {"type": "string"},
                                                        "prev": {"type": "string"},
                                                        "next": {"type": "string"},
                                                    },
                                                },
                                            },
                                        }
                                    },
                                }
                            }
                        },
                    }
                },
            },
        },
        "/factions/{id_}": {
            "get": {
                "summary": "GET Factions singular",
                "tags": ["Factions"],
                "parameters": [
                    {
                        "name": "id_",
                        "description": "identifier",
                        "in": "path",
                        "required": "true",
                    }
                ],
                "responses": {
                    "200": {
                        "description": "success",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/FactionSchema"}
                            }
                        },
                    }
                },
            },
            "patch": {},
            "delete": {},
        },
        "/factions/{id_}/units": {
            "get": {
                "summary": "GET Factions associated units (downstream route test)",
                "tags": ["Factions"],
                "parameters": [
                    {
                        "name": "id_",
                        "description": "identifier",
                        "in": "path",
                        "required": "true",
                    }
                ],
                "200": {
                    "description": "success",
                    "content": {"application/json": {"schema": {"type": "object"}}},
                },
            }
        },
        "/units": {
            "get": {
                "summary": "GET Units LIST",
                "tags": ["Units"],
                "responses": {
                    "200": {
                        "description": "success",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "data": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "type": {
                                                        "type": "string",
                                                        "example": "unit",
                                                    },
                                                    "id": {
                                                        "type": "string",
                                                        "format": "uuid",
                                                        "description": "Entity UUID",
                                                        "example": "b636a2e9-889a-4da9-bd2e-c52b50b5e5e2",
                                                    },
                                                    "attributes": {
                                                        "id": {"type": "string"},
                                                        "title": {"type": "string"},
                                                        "description": {
                                                            "type": "string"
                                                        },
                                                        "roster_slot": {
                                                            "type": "string"
                                                        },
                                                        "price": {"type": "string"},
                                                        "keywords": {
                                                            "type": "array",
                                                            "items": {"type": "string"},
                                                        },
                                                    },
                                                    "relationships": {
                                                        "type": "object",
                                                        "properties": {
                                                            "faction": {
                                                                "type": "object",
                                                                "properties": {
                                                                    "data": {
                                                                        "type": "object",
                                                                        "properties": {
                                                                            "type": {
                                                                                "type": "string"
                                                                            },
                                                                            "id": {
                                                                                "type": "string"
                                                                            },
                                                                        },
                                                                    }
                                                                },
                                                            }
                                                        },
                                                    },
                                                },
                                            },
                                        }
                                    },
                                }
                            }
                        },
                    }
                },
            },
            "post": {
                "summary": "POST a Unit",
                "tags": ["Units"],
                "requestBody": {"required": "true", "content": {}},
                "responses": {
                    "201": {
                        "description": "success",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "data": {
                                            "type": "object",
                                            "properties": {
                                                "type": {
                                                    "type": "string",
                                                    "example": "faction",
                                                },
                                                "id": {
                                                    "type": "string",
                                                    "format": "uuid",
                                                    "description": "Entity UUID",
                                                    "example": "b636a2e9-889a-4da9-bd2e-c52b50b5e5e2",
                                                },
                                                "attributes": {
                                                    "id": {"type": "string"},
                                                    "title": {"type": "string"},
                                                    "description": {"type": "string"},
                                                    "roster_slot": {"type": "string"},
                                                    "price": {"type": "string"},
                                                    "keywords": {
                                                        "type": "array",
                                                        "items": {"type": "string"},
                                                    },
                                                },
                                                "relationships": {
                                                    "type": "object",
                                                    "properties": {
                                                        "faction": {
                                                            "type": "object",
                                                            "properties": {
                                                                "data": {
                                                                    "type": "object",
                                                                    "properties": {
                                                                        "type": {
                                                                            "type": "string"
                                                                        },
                                                                        "id": {
                                                                            "type": "string"
                                                                        },
                                                                    },
                                                                }
                                                            },
                                                        }
                                                    },
                                                },
                                                "links": {
                                                    "type": "object",
                                                    "description": "Links Object",
                                                    "properties": {
                                                        "self": {"type": "string"},
                                                        "prev": {"type": "string"},
                                                        "next": {"type": "string"},
                                                    },
                                                },
                                            },
                                        }
                                    },
                                }
                            }
                        },
                    }
                },
            },
        },
        "/units/{id_}": {
            "get": {
                "summary": "GET Units singular",
                "tags": ["Units"],
                "responses": {
                    "200": {
                        "description": "success",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "data": {
                                            "type": "object",
                                            "properties": {
                                                "type": {
                                                    "type": "string",
                                                    "example": "faction",
                                                },
                                                "id": {
                                                    "type": "string",
                                                    "format": "uuid",
                                                    "description": "Entity UUID",
                                                    "example": "b636a2e9-889a-4da9-bd2e-c52b50b5e5e2",
                                                },
                                                "attributes": {
                                                    "type": "object",
                                                    "properties": {
                                                        "id": {"type": "string"},
                                                        "title": {"type": "string"},
                                                        "description": {
                                                            "type": "string"
                                                        },
                                                        "roster_slot": {
                                                            "type": "string"
                                                        },
                                                        "price": {"type": "string"},
                                                        "keywords": {
                                                            "type": "array",
                                                            "items": {"type": "string"},
                                                        },
                                                    },
                                                },
                                                "relationships": {
                                                    "type": "object",
                                                    "properties": {
                                                        "faction": {
                                                            "type": "object",
                                                            "properties": {
                                                                "data": {
                                                                    "type": "object",
                                                                    "properties": {
                                                                        "type": {
                                                                            "type": "string"
                                                                        },
                                                                        "id": {
                                                                            "type": "string"
                                                                        },
                                                                    },
                                                                }
                                                            },
                                                        }
                                                    },
                                                },
                                                "links": {
                                                    "type": "object",
                                                    "description": "Links Object",
                                                    "properties": {
                                                        "self": {"type": "string"},
                                                        "prev": {"type": "string"},
                                                        "next": {"type": "string"},
                                                    },
                                                },
                                            },
                                        }
                                    },
                                }
                            }
                        },
                    }
                },
            },
            "patch": {},
            "delete": {},
        },
        "/units/{id_}/get_skus/{type_name}": {"get": {}},
        "/insufficient_model": {
            "get": {
                "summary": "GET LIST for an incomplete model",
                "tags": ["InsufficientModel"],
                "responses": {
                    "200": {
                        "description": "success",
                        "content": {"application/json": {"schema": {"type": "object"}}},
                    }
                },
            }
        },
        "/insufficient_model/{id_}": {
            "get": {
                "summary": "GET ONE for an incomplete model",
                "tags": ["InsufficientModel"],
                "responses": {
                    "200": {
                        "description": "success",
                        "content": {"application/json": {"schema": {"type": "object"}}},
                    }
                },
            }
        },
    },
    "components": {
        "FactionSchema": {
            "type": "object",
            "properties": {
                "data": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string", "example": "faction"},
                        "id": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Entity UUID",
                            "example": "b636a2e9-889a-4da9-bd2e-c52b50b5e5e2",
                        },
                        "attributes": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "title": {"type": "string"},
                                "description": {"type": "string"},
                                "keywords": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                            },
                        },
                        "relationships": {
                            "type": "object",
                            "properties": {
                                "units": {
                                    "type": "object",
                                    "properties": {
                                        "data": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "type": {"type": "string"},
                                                    "id": {"type": "string"},
                                                },
                                            },
                                        }
                                    },
                                }
                            },
                        },
                        "links": {
                            "type": "object",
                            "description": "Links Object",
                            "properties": {
                                "self": {"type": "string"},
                                "prev": {"type": "string"},
                                "next": {"type": "string"},
                            },
                        },
                    },
                }
            },
        }
    },
}


def get_testing_spec():
    return testing_openapi_spec
