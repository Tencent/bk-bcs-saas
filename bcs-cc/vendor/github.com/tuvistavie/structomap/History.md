# 0.6.1 / 2015-05-23

* Fix `TransformArray` bug with empty arrays

# 0.6.0 / 2015-05-21

* Rename package to structomap

# 0.5.0 / 2015-05-19

* Change `TransformArray` to accept `interface{}` instead of `[]interface{}`
* Add `MustTransformArray`, panicking version of `TransformArray`

# 0.4.0 / 2015-05-15

* Change `Result` method to `Transform` method.
* Improve reusability of serializers.

# 0.3.0 / 2015-05-15

* Replace `Convert` by `PickFunc` and `ConvertIf` by `PickFuncIf`.

# 0.2.1 / 2015-05-15

* Add support for `snake_case` and `camelCase`

# 0.2.0 / 2015-05-14

* Make `serializer.Serializer` an interface
* Export `serializer.Base` as a base serializer type

# 0.1.0 / 2015-05-13

* Initial release
