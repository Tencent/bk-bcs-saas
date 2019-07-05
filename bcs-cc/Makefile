VERSION := 1.0.0

BASEDIR := $(shell pwd)
PROJECTNAME := bcs_cc

# filter
SOURCEFILES := $(shell find . -type f -name "*.go" -not -path "./vendor/*" -not -path "./src/*"  -not -path "./editions/*" -not -path "./contrib/*" -print)

# init the dir for golang project
BUILDSRCDIR := ${BASEDIR}/src
BUILDPKGDIR := ${BASEDIR}/pkg
BUILDDIR := ${BASEDIR}/bin
BUILDTARGET := ${BUILDDIR}/bcs_cc

GOPATH := ${BASEDIR}
GO15VENDOREXPERIMENT := 1
GOENV := GOPATH=${GOPATH} GO15VENDOREXPERIMENT=${GO15VENDOREXPERIMENT}

# json package
BUILDARGS := -tags=jsoniter
LDFLAGS := -X bcs_cc/config.Edition=default -X bcs_cc/config.Version=${VERSION} -X bcs_cc/config.BuildTime=`date +%Y-%m-%dT%T%z`
DEBUGLDFLAGS := -n -X bcs_cc/config.Mode=debug ${LDFLAGS}
RELEASELDFLAGS := -s -w -X bcs_cc/config.Mode=release ${LDFLAGS}


.PHONY: build
build: ${BUILDDIR} ${BUILDSRCDIR} ${SOURCEFILES}
	${GOENV} go build ${BUILDARGS} -i -ldflags "${DEBUGLDFLAGS}" -o ${BUILDTARGET} ${PROJECTNAME}

.PHONY: release
release: ${BUILDDIR} ${BUILDSRCDIR}
	${GOENV} go build ${BUILDARGS} -v -ldflags "${RELEASELDFLAGS}" -o ${BUILDTARGET} ${PROJECTNAME}

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
	cd tests; ${GOENV} go test

.PHONY: codecheck
codecheck:
	${GOENV} find . -type f -name "*.go" -not -path "./vendor/*" -not -path "./src/*" -exec gofmt -d {} \; -exec golint {} \;


.PHONY: migrations
migrations:
	sh ${BASEDIR}/storage/migrations/template.sh ${BASEDIR}/storage/migrations

.PHONY: go-env
go-env:
	@${GOENV} go env

.PHONY: clean
clean:
	rm -rf ${BUILDSRCDIR} || true
	rm -rf ${BUILDTARGET} || true
	rm -rf ${BUILDPKGDIR} || true