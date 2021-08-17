# structomap [![Build Status](https://travis-ci.org/danhper/structomap.svg)](https://travis-ci.org/danhper/structomap) [![Coverage Status](https://coveralls.io/repos/danhper/structomap/badge.svg?branch=master)](https://coveralls.io/r/danhper/structomap?branch=master) [![GoDoc](https://godoc.org/github.com/danhper/structomap?status.svg)](https://godoc.org/github.com/danhper/structomap)

This package helps you to transform your `struct` into `map` easily. It provides a `structomap.Serializer` interface implemented by the `structomap.Base` type which contains chainable function to add, remove or modify fields. The `struct` is transformed to a `map[string]interface{}` using the `Transform(entity interface{})` method.
It is then up to you to encode the result in JSON, XML or whatever you like.

Here is an example.

```go
import "github.com/danhper/structomap"

type User struct {
    ID        int
    Email     string
    HideEmail bool
    FirstName string
    LastName  string
    CreatedAt time.Time
    UpdatedAt time.Time
}

currentTime := time.Date(2015, 05, 13, 15, 30, 0, 0, time.UTC)

user := User{
    ID: 1, Email: "x@example.com", FirstName: "Foo", LastName:  "Bar",
    HideEmail: true, CreatedAt: currentTime, UpdatedAt: currentTime,
}
userSerializer := structomap.New().
              UseSnakeCase().
              Pick("ID", "FirstName", "LastName", "Email").
              PickFunc(func(t interface{}) interface{} {
                  return t.(time.Time).Format(time.RFC3339)
              }, "CreatedAt", "UpdatedAt").
              OmitIf(func(u interface{}) bool {
                  return u.(User).HideEmail
              }, "Email").
              Add("CurrentTime", time.Date(2015, 5, 15, 17, 41, 0, 0, time.UTC)).
              AddFunc("FullName", func(u interface{}) interface{} {
                  return u.(User).FirstName + " " + u.(User).LastName
              })

userMap := userSerializer.Transform(user)
str, _ := json.MarshalIndent(userMap, "", "  ")
fmt.Println(string(str))
```

will give:

```json
{
  "created_at": "2015-05-13T15:30:00Z",
  "current_time": "2015-05-15T17:41:00Z",
  "first_name": "Foo",
  "full_name": "Foo Bar",
  "id": 1,
  "last_name": "Bar",
  "updated_at": "2015-05-13T15:30:00Z"
}
```


## Working with slices and arrays

You can also use structomap to transform slices and arrays, it will be applied to
all elements. The only thing to do is to call `TransformArray(entities)` on a slice or an array. As `TransformArray` expects an `interface{}`, but in fact
really wants a slice or an array, a second `error` argument is returned. If you do not want it, you can use `MustTransformArray`, which will panic instead of returning an error.

Here in an example reusing the above serializer.

```go
otherUser := User{ID: 2, FirstName: "Ping", LastName: "Pong", CreatedAt: createdAt, UpdatedAt: createdAt}
users := []User{user, otherUser}
result, _ := userSerializer.TransformArray(users)
str, _ := json.MarshalIndent(result, "", "  ")
fmt.Println(string(str))
```

This will give:

```json
[
  {
    "created_at": "2015-05-13T15:30:00Z",
    "current_time": "2015-05-15T17:41:00Z",
    "first_name": "Foo",
    "full_name": "Foo Bar",
    "id": 1,
    "last_name": "Bar",
    "updated_at": "2015-05-13T15:30:00Z"
  },
  {
    "created_at": "2015-05-13T15:30:00Z",
    "current_time": "2015-05-15T17:41:00Z",
    "email": "",
    "first_name": "Ping",
    "full_name": "Ping Pong",
    "id": 2,
    "last_name": "Pong",
    "updated_at": "2015-05-13T15:30:00Z"
  }
]
```


## Choosing a key format

You can set the key format for the output map using `UseSnakeCase()`, `UsePascalCase()` or `UseCamelCase()` on the serializer object.
You can also set the default case for all new serializers by using
`structomap.SetDefaultCase(structomap.SnakeCase)` (`structomap.CamelCase` and `structomap.PascalCase` are also available). The `init()` function would be a good place to set this.

## Building your own serializer

With `structomap.Base` as a base, you can easily build your serializer.

```go
type UserSerializer struct {
  *structomap.Base
}

func NewUserSerializer() *UserSerializer {
  u := &UserSerializer{structomap.New()}
  u.Pick("ID", "CreatedAt", "UpdatedAt", "DeletedAt")
  return u
}

func (u *UserSerializer) WithPrivateInfo() *UserSerializer {
  u.Pick("Email")
  return u
}

userMap := NewUserSerializer().WithPrivateInfo().Transform(user)
```

Note that the `u.Pick`, and all other methods do modify the serializer, they do not return a new serializer each time. This is why it works
even when ignoring `u.Pick` return value.

## License

This is released under the MIT license. See the [LICENSE](./LICENSE) file for more information.

## Godoc

The full documentation is available at https://godoc.org/github.com/danhper/structomap.
