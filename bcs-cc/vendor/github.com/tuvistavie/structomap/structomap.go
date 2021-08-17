// Package structomap contains
package structomap

import (
	"fmt"
	"reflect"

	"github.com/fatih/structs"
	"github.com/huandu/xstrings"
)

// KeyCase represenets the word case of the output keys
type KeyCase int

const (
	// NotSet uses the original case for keys
	NotSet KeyCase = iota

	// CamelCase uses camelCase keys
	CamelCase = iota

	// PascalCase Uses PascalCase keys
	PascalCase = iota

	// SnakeCase uses snake_case keys
	SnakeCase = iota
)

var defaultCase = NotSet

// SetDefaultCase set the default key case (snake_case, camelCase or PascalCase) for
// all new serializers
func SetDefaultCase(caseType KeyCase) {
	defaultCase = caseType
}

type mapModifier func(jsonMap) jsonMap

type jsonMap map[string]interface{}

// Predicate is an alias for func(interface{}) bool used to test for inclusion
type Predicate func(interface{}) bool

// KeyConverter is an alias for func(string) string used to transform keys
type KeyConverter func(string) string

// ValueConverter is an alias for func(interface{}) interface{} used to transform values
type ValueConverter func(interface{}) interface{}

// Serializer is the base interface containing all serialization methods
type Serializer interface {
	Transform(entity interface{}) map[string]interface{}
	TransformArray(entities interface{}) ([]map[string]interface{}, error)
	MustTransformArray(entities interface{}) []map[string]interface{}
	ConvertKeys(keyConverter KeyConverter) Serializer
	UseSnakeCase() Serializer
	UseCamelCase() Serializer
	UsePascalCase() Serializer
	PickAll() Serializer
	Pick(keys ...string) Serializer
	PickIf(predicate Predicate, keys ...string) Serializer
	PickFunc(converter ValueConverter, keys ...string) Serializer
	PickFuncIf(predicate Predicate, converter ValueConverter, keys ...string) Serializer
	Omit(keys ...string) Serializer
	OmitIf(predicate Predicate, keys ...string) Serializer
	Add(key string, value interface{}) Serializer
	AddIf(predicate Predicate, key string, value interface{}) Serializer
	AddFunc(key string, converter ValueConverter) Serializer
	AddFuncIf(predicate Predicate, key string, converter ValueConverter) Serializer
}

func alwaysTrue(u interface{}) bool {
	return true
}

func alwaysFalse(u interface{}) bool {
	return false
}

func identity(u interface{}) interface{} {
	return u
}

// Base is a basic implementation of Serializer
type Base struct {
	raw          interface{}
	modifiers    []mapModifier
	reflected    reflect.Value
	keyConverter KeyConverter
}

// New creates a new serializer
func New() *Base {
	b := &Base{}
	b.addDefaultKeyConverter()
	return b
}

// Transform transforms the entity into a map[string]interface{} ready to be serialized
func (b *Base) Transform(entity interface{}) map[string]interface{} {
	b.raw = entity
	b.reflected = reflect.Indirect(reflect.ValueOf(entity))
	return b.result()
}

// TransformArray transforms the entities into a []map[string]interface{} array
// ready to be serialized. Entities must be a slice or an array
func (b *Base) TransformArray(entities interface{}) ([]map[string]interface{}, error) {
	s := reflect.ValueOf(entities)
	if s.Kind() != reflect.Slice && s.Kind() != reflect.Array {
		return nil, fmt.Errorf("TransformArray() given a non-slice type")
	}
	result := []map[string]interface{}{}
	for i := 0; i < s.Len(); i++ {
		result = append(result, b.Transform(s.Index(i).Interface()))
	}
	return result, nil
}

// MustTransformArray transforms the entities into a []map[string]interface{}
// array ready to be serialized. Panics if entities is not a slice or an array
func (b *Base) MustTransformArray(entities interface{}) []map[string]interface{} {
	res, err := b.TransformArray(entities)
	if err != nil {
		panic(err)
	}
	return res
}

func (b *Base) addDefaultKeyConverter() {
	switch defaultCase {
	case PascalCase:
		b.UsePascalCase()
	case SnakeCase:
		b.UseSnakeCase()
	case CamelCase:
		b.UseCamelCase()
	default:
		break
	}
}

func (b *Base) transformedResult(result jsonMap) jsonMap {
	newResult := make(map[string]interface{})
	for key, value := range result {
		newResult[b.keyConverter(key)] = value
	}
	return newResult
}

func (b *Base) result() map[string]interface{} {
	result := make(map[string]interface{})
	for _, modifier := range b.modifiers {
		result = modifier(result)
	}
	if b.keyConverter != nil {
		return b.transformedResult(result)
	}
	return result
}

// ConvertKeys converts all the keys using the given converter
func (b *Base) ConvertKeys(keyConverter KeyConverter) Serializer {
	b.keyConverter = keyConverter
	return b
}

// UsePascalCase uses PascalCase keys for the serializer
func (b *Base) UsePascalCase() Serializer {
	return b.ConvertKeys(func(k string) string {
		return xstrings.ToCamelCase(xstrings.ToSnakeCase(k))
	})
}

// UseCamelCase uses camelCase keys for the serializer
func (b *Base) UseCamelCase() Serializer {
	return b.ConvertKeys(func(k string) string {
		return xstrings.FirstRuneToLower(xstrings.ToCamelCase(xstrings.ToSnakeCase(k)))
	})
}

// UseSnakeCase uses snake_case keys for the serializer
func (b *Base) UseSnakeCase() Serializer {
	return b.ConvertKeys(xstrings.ToSnakeCase)
}

// PickAll adds all the exported fields to the result
func (b *Base) PickAll() Serializer {
	b.modifiers = append(b.modifiers, func(m jsonMap) jsonMap {
		return structs.Map(b.raw)
	})
	return b
}

// Pick adds the given fields to the result
func (b *Base) Pick(keys ...string) Serializer {
	return b.PickFunc(identity, keys...)
}

// PickIf adds the given fields to the result if the Predicate returns true
func (b *Base) PickIf(p Predicate, keys ...string) Serializer {
	return b.PickFuncIf(p, identity, keys...)
}

// PickFunc adds the given fields to the result after applying the converter
func (b *Base) PickFunc(converter ValueConverter, keys ...string) Serializer {
	return b.PickFuncIf(alwaysTrue, converter, keys...)
}

// PickFuncIf adds the given fields to the result after applying the converter if the predicate returns true
func (b *Base) PickFuncIf(p Predicate, converter ValueConverter, keys ...string) Serializer {
	b.modifiers = append(b.modifiers, func(m jsonMap) jsonMap {
		if p(b.raw) {
			for _, key := range keys {
				m[key] = converter(b.reflected.FieldByName(key).Interface())
			}
		}
		return m
	})
	return b
}

// Omit omits the given fields from the result
func (b *Base) Omit(keys ...string) Serializer {
	return b.OmitIf(alwaysTrue, keys...)
}

// OmitIf omits the given fields from the result if the Predicate returns true
func (b *Base) OmitIf(p Predicate, keys ...string) Serializer {
	b.modifiers = append(b.modifiers, func(m jsonMap) jsonMap {
		if p(b.raw) {
			for _, key := range keys {
				delete(m, key)
			}
		}
		return m
	})
	return b
}

// Add adds a custom field to the result
func (b *Base) Add(key string, value interface{}) Serializer {
	return b.AddIf(alwaysTrue, key, value)
}

// AddIf adds a custom field to the result if the Predicate returns true
func (b *Base) AddIf(p Predicate, key string, value interface{}) Serializer {
	return b.AddFuncIf(p, key, func(m interface{}) interface{} { return value })
}

// AddFunc adds a computed custom field to the result
func (b *Base) AddFunc(key string, f ValueConverter) Serializer {
	return b.AddFuncIf(alwaysTrue, key, f)
}

// AddFuncIf adds a computed custom field to the result if the Predicate returns true
func (b *Base) AddFuncIf(p Predicate, key string, f ValueConverter) Serializer {
	b.modifiers = append(b.modifiers, func(m jsonMap) jsonMap {
		if p(b.raw) {
			m[key] = f(b.raw)
		}
		return m
	})
	return b
}
