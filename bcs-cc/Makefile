VERSION := 1.0.0

BASEDIR := $(shell pwd)
PROJECTNAME := bcs-cc

# filter
SOURCEFILES := $(shell find . -type f -name "*.go" -not -path "./vendor/*" -not -path "./src/*"  -not -path "./editions/*" -not -path "./contrib/*" -print)

# init the dir for golang project
BUILDSRCDIR := ${BASEDIR}/src
BUILDPKGDIR := ${BASEDIR}/pkg
BUILDDIR := ${BASEDIR}/bin
BUILDTARGET := ${BUILDDIR}/bcs-cc

GOPATH := ${BASEDIR}
GOENV := GOPATH=${GOPATH}

# json package
BUILDARGS := -tags=jsoniter
LDFLAGS := -X bcs-cc/config.Edition=default -X bcs-cc/config.Version=${VERSION} -X bcs-cc/config.BuildTime=`date +%Y-%m-%dT%T%z`
DEBUGLDFLAGS := -n -X bcs-cc/config.Mode=debug ${LDFLAGS}
RELEASELDFLAGS := -s -w -X bcs-cc/config.Mode=release ${LDFLAGS}


.PHONY: build
build: ${BUILDDIR} ${SOURCEFILES}
	go build ${BUILDARGS} -ldflags "${DEBUGLDFLAGS}" -o ${BUILDTARGET} ${PROJECTNAME}

.PHONY: release
release: ${BUILDDIR} ${BUILDSRCDIR}
	go build ${BUILDARGS} -v -ldflags "${RELEASELDFLAGS}" -o ${BUILDTARGET} ${PROJECTNAME}

${BUILDDIR}:
	mkdir -p ${BUILDPKGDIR}
	mkdir -p ${BUILDDIR}

${BUILDSRCDIR}:
	mkdir -p ${BUILDSRCDIR}
	ln -s ${BASEDIR} ${BUILDSRCDIR}/${PROJECTNAME}

.PHONY: dev-init
dev-init: ${BUILDDIR} ${BUILDSRCDIR}

.PHONY: test
test:
	cd tests; go test

.PHONY: codecheck
codecheck:
	find . -type f -name "*.go" -not -path "./vendor/*" -not -path "./src/*" -exec gofmt -d {} \; -exec golint {} \;


.PHONY: migrations
migrations:
	sh ${BASEDIR}/storage/migrations/template.sh ${BASEDIR}/storage/migrations

.PHONY: go-env
go-env:
	go env

.PHONY: clean
clean:
	rm -rf ${BUILDSRCDIR} || true
	rm -rf ${BUILDTARGET} || true
	rm -rf ${BUILDPKGDIR} || true