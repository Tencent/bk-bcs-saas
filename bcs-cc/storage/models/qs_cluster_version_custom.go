package models

type functionTypeForBaseVersion func(BaseVersionQuerySet, string, string) BaseVersionQuerySet

// Filter : filter with field
func (qs BaseVersionQuerySet) Filter(fields map[string]string, f functionTypeForBaseVersion) BaseVersionQuerySet {
	for field, val := range fields {
		if val == "" {
			continue
		}
		qs = f(qs, field, val)
	}
	return qs
}

// function for query
func baseVersionFilterString(qs BaseVersionQuerySet, field string, val string) BaseVersionQuerySet {
	switch field {
	case "version":
		return qs.VersionEq(val)
	case "environment":
		return qs.EnvironmentEq(val)
	case "kind":
		return qs.KindEq(val)
	}
	return qs
}
