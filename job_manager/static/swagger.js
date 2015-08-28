{
  "swagger": "2.0",
  "info": {
    "version": "1.0.0",
    "title": "Cumulonimbi Job Manager API",
    "description": "The API for consumers of Cumulonimbi to use",
    "termsOfService": "http://example.com",
    "contact": {
      "name": "Pim Witlox & Johannes Bertens"
    },
    "license": {
      "name": "proprietary"
    }
  },
  "host": "localhost:5000",
  "basePath": "/",
  "schemes": [
    "http"
  ],
  "consumes": [
    "application/json"
  ],
  "produces": [
    "application/json"
  ],
  "paths": {
    "/jobs": {
      "get": {
        "description": "Returns all jobs that the user has access to",
        "produces": [
          "application/json"
        ],
        "responses": {
          "200": {
            "description": "A list of jobs.",
            "schema": {
              "type": "array",
              "items": {
                "$ref": "#/definitions/Job"
              }
            }
          }
        }
      },
      "delete": {
        "description": "Deletes all jobs that the user has access to",
        "produces": [
          "application/json"
        ],
        "responses": {
          "200": {
            "description": "Output"
          }
        }
      },
      "post": {
        "description": "Creates a new job.",
        "operationId": "addJob",
        "produces": [
          "application/json"
        ],
        "parameters": [
          {
            "name": "job",
            "in": "body",
            "description": "Job to add",
            "required": true,
            "schema": {
              "$ref": "#/definitions/JobInput"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "job response",
            "schema": {
              "$ref": "#/definitions/Job"
            }
          },
          "default": {
            "description": "unexpected error",
            "schema": {
              "$ref": "#/definitions/ErrorModel"
            }
          }
        }
      }
    }
  },
  "definitions": {
    "Job": {
      "type": "object",
      "required": [
        "id"
      ],
      "properties": {
        "status": {
          "type": "string"
        },
        "graph": {
          "type": "string"
        },
        "_id": {
          "type": "object"
        },
        "name": {
          "type": "string"
        }
      }
    },
    "JobInput": {
      "type": "object",
      "required": [
        "job_name",
        "graph"
      ],
      "properties": {
        "job_name": {
          "type": "string"
        },
        "graph": {
          "type": "string"
        }
      }
    }
  }
}