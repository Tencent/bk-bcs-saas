// Package goreq is a simplified http client.
// Its initial codes are cloned from [HttpRequest](https://github.com/parnurzeal/gorequest). I have refactored the codes and make it more friendly to programmers.  And some bugs are fixed and new features are added.
// goreq makes http thing more simple for you, using fluent styles to make http client more awesome. You can control headers, timeout, query parameters, binding response and others in one line:
//
// Before
//
// client := &http.Client{
// 	 CheckRedirect: redirectPolicyFunc,
// }
// req, err := http.NewRequest("GET", "http://example.com", nil)
// req.Header.Add("If-None-Match", `W/"wyzzy"`)
// resp, err := client.Do(req)
//
// Using GoReq
//
// resp, body, errs := goreq.New().Get("http://example.com").
//   RedirectPolicy(redirectPolicyFunc).
//   SetHeader("If-None-Match", `W/"wyzzy"`).
//   End()
package utils

import (
	"bytes"
	"crypto/tls"
	"encoding/json"
	"errors"
	"io/ioutil"
	"log"
	"mime/multipart"
	"net"
	"net/http"
	"net/http/cookiejar"
	"net/http/httputil"
	"net/url"
	"os"
	"reflect"
	"strings"
	"time"

	"github.com/moul/http2curl"
	"github.com/weppos/publicsuffix-go/publicsuffix"
	"golang.org/x/net/proxy"
)

// Request represents an HTTP request received by a server
// or to be sent by a client.
type Request *http.Request

// Response represents the response from an HTTP request.
type Response *http.Response

// HTTP methods we support
const (
	POST    = "POST"
	GET     = "GET"
	HEAD    = "HEAD"
	PUT     = "PUT"
	DELETE  = "DELETE"
	PATCH   = "PATCH"
	OPTIONS = "OPTIONS"
)

// A GoReq is a object storing all request data for client.
type GoReq struct {
	URL              string
	Host             string
	Method           string
	Header           map[string]string
	Data             map[string]interface{}
	Params           string
	FormData         url.Values
	QueryData        url.Values
	RawStringData    string
	RawBytesData     []byte
	FilePath         string
	FileParam        string
	Client           *http.Client
	CheckRedirect    func(r *http.Request, v []*http.Request) error
	Transport        *http.Transport
	Cookies          []*http.Cookie
	Errors           []error
	BasicAuth        struct{ Username, Password string }
	Debug            bool
	CurlCommand      bool
	logger           *log.Logger
	retry            *RetryConfig
	bindResponseBody interface{}
	Timeout          time.Duration
}

// RetryConfig is used to config retry parameters
type RetryConfig struct {
	//Max retry count
	RetryCount int
	//Retry timeout
	RetryTimeout int
	// Retry only when received those http status
	RetryOnHTTPStatus []int
}

// NewRequest : New returns a new GoReq object.
func NewRequest() *GoReq {
	gr := &GoReq{
		Data:             make(map[string]interface{}),
		Header:           make(map[string]string),
		FormData:         url.Values{},
		QueryData:        url.Values{},
		Client:           nil,
		Transport:        &http.Transport{},
		Cookies:          make([]*http.Cookie, 0),
		Errors:           nil,
		BasicAuth:        struct{ Username, Password string }{},
		Debug:            false,
		CurlCommand:      false,
		logger:           log.New(os.Stderr, "[goreq]", log.LstdFlags),
		retry:            &RetryConfig{RetryCount: 0, RetryTimeout: 0, RetryOnHTTPStatus: nil},
		bindResponseBody: nil,
	}
	return gr
}

// SetDebug enables the debug mode which logs request/response detail
func (gr *GoReq) SetDebug(enable bool) *GoReq {
	gr.Debug = enable
	return gr
}

// SetCurlCommand enables the curlcommand mode which display a CURL command line
func (gr *GoReq) SetCurlCommand(enable bool) *GoReq {
	gr.CurlCommand = enable
	return gr
}

// SetLogger is used to set a Logger
func (gr *GoReq) SetLogger(logger *log.Logger) *GoReq {
	gr.logger = logger
	return gr
}

// SetClient ise used to set a shared http.Client
func (gr *GoReq) SetClient(client *http.Client) *GoReq {
	gr.Client = client
	return gr
}

func (gr *GoReq) setDefaultClient() *GoReq {
	cookiejarOptions := cookiejar.Options{
		PublicSuffixList: publicsuffix.CookieJarList,
	}
	jar, _ := cookiejar.New(&cookiejarOptions)
	client := &http.Client{Jar: jar}
	gr.Client = client
	return gr
}

// Reset is used to clear GoReq data for another new request only keep client and logger.
func (gr *GoReq) Reset() *GoReq {
	gr.URL = ""
	gr.Method = ""
	gr.Header = make(map[string]string)
	gr.Data = make(map[string]interface{})
	gr.FormData = url.Values{}
	gr.QueryData = url.Values{}
	gr.RawStringData = ""
	gr.RawBytesData = make([]byte, 0)
	gr.FilePath = ""
	gr.FileParam = ""
	gr.Cookies = make([]*http.Cookie, 0)
	gr.Errors = nil
	gr.retry = &RetryConfig{RetryCount: 0, RetryTimeout: 0, RetryOnHTTPStatus: nil}
	gr.bindResponseBody = nil
	return gr
}

// Get is used to set GET HttpMethod with a url.
func (gr *GoReq) Get(targetURL string) *GoReq {
	//gr.Reset()
	gr.Method = GET
	gr.URL = targetURL
	gr.Errors = nil
	return gr
}

// Post is used to set POST HttpMethod with a url.
func (gr *GoReq) Post(targetURL string) *GoReq {
	//gr.Reset()
	gr.Method = POST
	gr.URL = targetURL
	gr.Errors = nil
	return gr
}

// Head is used to set HEAD HttpMethod with a url.
func (gr *GoReq) Head(targetURL string) *GoReq {
	//gr.Reset()
	gr.Method = HEAD
	gr.URL = targetURL
	gr.Errors = nil
	return gr
}

// Put is used to set PUT HttpMethod with a url.
func (gr *GoReq) Put(targetURL string) *GoReq {
	//gr.Reset()
	gr.Method = PUT
	gr.URL = targetURL
	gr.Errors = nil
	return gr
}

// Delete is used to set DELETE HttpMethod with a url.
func (gr *GoReq) Delete(targetURL string) *GoReq {
	//gr.Reset()
	gr.Method = DELETE
	gr.URL = targetURL
	gr.Errors = nil
	return gr
}

// Patch is used to set PATCH HttpMethod with a url.
func (gr *GoReq) Patch(targetURL string) *GoReq {
	//gr.Reset()
	gr.Method = PATCH
	gr.URL = targetURL
	gr.Errors = nil
	return gr
}

// Options is used to set OPTIONS HttpMethod with a url.
func (gr *GoReq) Options(targetURL string) *GoReq {
	//gr.Reset()
	gr.Method = OPTIONS
	gr.URL = targetURL
	gr.Errors = nil
	return gr
}

// SetHeader is used for setting header fields.
// Example. To set `Accept` as `application/json`
//
//    goreq.New().
//      Post("/gamelist").
//      SetHeader("Accept", "application/json").
//      End()
func (gr *GoReq) SetHeader(param string, value string) *GoReq {
	gr.Header[param] = value
	return gr
}

// SetHeaders is used to set headers with multiple fields.
// it accepts structs or json strings:
// for example:
//    New().Get(ts.URL).
//    SetHeaders(`{'Content-Type' = 'text/plain','X-Test-Tag'='test'}`).
//    End()
//or
//    headers := struct {
//        ContentType string `json:"Content-Type"`
//        XTestTag string `json:"X-Test-Tag"`
//    } {ContentType:"text/plain",XTestTag:"test"}
//
//    New().Get(ts.URL).
//    SetHeaders(headers).
//    End()
//
func (gr *GoReq) SetHeaders(headers interface{}) *GoReq {
	switch v := reflect.ValueOf(headers); v.Kind() {
	case reflect.String:
		gr.setJSONHeaders(v.String())
	case reflect.Struct:
		gr.setStructHeaders(v.Interface())
	default:
	}
	return gr
}

func (gr *GoReq) setStructHeaders(headers interface{}) *GoReq {
	if marshalContent, err := json.Marshal(headers); err != nil {
		gr.Errors = append(gr.Errors, err)
	} else {
		var val map[string]string
		if err := json.Unmarshal(marshalContent, &val); err != nil {
			gr.Errors = append(gr.Errors, err)
		} else {
			for k, v := range val {
				gr.Header[k] = v
			}
		}
	}
	return gr
}

func (gr *GoReq) setJSONHeaders(headers string) *GoReq {
	var val map[string]string
	if err := json.Unmarshal([]byte(headers), &val); err == nil {
		for k, v := range val {
			gr.Header[k] = v
		}
	} else {
		gr.Errors = append(gr.Errors, err)
	}
	return gr
}

// SetBasicAuth sets the basic authentication header
// Example. To set the header for username "myuser" and password "mypass"
//
//    goreq.New()
//      Post("/gamelist").
//      SetBasicAuth("myuser", "mypass").
//      End()
func (gr *GoReq) SetBasicAuth(username string, password string) *GoReq {
	gr.BasicAuth = struct{ Username, Password string }{username, password}
	return gr
}

// AddCookie adds a cookie to the request. The behavior is the same as AddCookie on Request from net/http
func (gr *GoReq) AddCookie(c *http.Cookie) *GoReq {
	gr.Cookies = append(gr.Cookies, c)
	return gr
}

// AddCookies is a convenient method to add multiple cookies
func (gr *GoReq) AddCookies(cookies []*http.Cookie) *GoReq {
	gr.Cookies = append(gr.Cookies, cookies...)
	return gr
}

// ShortContentTypes defines some short content types.
var ShortContentTypes = map[string]string{
	"html":       "text/html",
	"text":       "text/plain",
	"json":       "application/json",
	"xml":        "application/xml",
	"urlencoded": "application/x-www-form-urlencoded",
	"form":       "application/x-www-form-urlencoded",
	"form-data":  "application/x-www-form-urlencoded",
	"stream":     "application/octet-stream",
}

// ContentType is a convenience function to specify the data type to send instead of SetHeader("Content-Type", "......").
// For example, to send data as `application/x-www-form-urlencoded` :
//
//    goreq.New().
//      Post("/recipe").
//      ContentType("application/json").
//      SendMapString(`{ "name": "egg benedict", "category": "brunch" }`).
//      End()
//
// This will POST the body "name=egg benedict&category=brunch" to url /recipe
// GoReq supports abbreviation Types:
//
//    "html" as "text/html"
//    "text" as "text/plain"
//    "json" as "application/json" uses
//    "xml" as "application/xml"
//    "urlencoded", "form" or "form-data" as "application/x-www-form-urlencoded"
//    "stream" as "application/octet-stream"
//
func (gr *GoReq) ContentType(typeStr string) *GoReq {
	if ShortContentTypes[typeStr] != "" {
		typeStr = ShortContentTypes[typeStr]
	}
	gr.Header["Content-Type"] = typeStr
	return gr
}

// Query function accepts either json string or query strings which will form a query-string in url of GET method or body of POST method.
// For example, making "/search?query=bicycle&size=50x50&weight=20kg" using GET method:
//
//      goreq.New().
//        Get("/search").
//        Query(`{ "query": "bicycle" }`).
//        Query(`{ "size": "50x50" }`).
//        Query(`{ "weight": "20kg" }`).
//        End()
//
// Or you can put multiple json values:
//
//      goreq.New().
//        Get("/search").
//        Query(`{ "size": "50x50", "weight":"20kg" }`).
//        End()
//
// Strings are also acceptable:
//
//      goreq.New().
//        Get("/search").
//        Query("query=bicycle&size=50x50").
//        Query("weight=20kg").
//        End()
//
// Or even Mixed! :)
//
//      goreq.New().
//        Get("/search").
//        Query("query=bicycle").
//        Query(`{ "size": "50x50", "weight":"20kg" }`).
//        End()
//
func (gr *GoReq) Query(content interface{}) *GoReq {
	switch v := reflect.ValueOf(content); v.Kind() {
	case reflect.String:
		gr.queryString(v.String())
	case reflect.Struct:
		gr.queryStruct(v.Interface())
	default:
	}
	return gr
}

func (gr *GoReq) BindHost(host string) *GoReq {
	gr.Host = host
	return gr
}

//create queryData by parsing structs.
func (gr *GoReq) queryStruct(content interface{}) *GoReq {
	if marshalContent, err := json.Marshal(content); err != nil {
		gr.Errors = append(gr.Errors, err)
	} else {
		var val map[string]interface{}
		if err := json.Unmarshal(marshalContent, &val); err != nil {
			gr.Errors = append(gr.Errors, err)
		} else {
			for k, v := range val {
				gr.QueryData.Add(k, v.(string))
			}
		}
	}
	return gr
}

func (gr *GoReq) queryString(content string) *GoReq {
	var val map[string]string
	if err := json.Unmarshal([]byte(content), &val); err == nil {
		for k, v := range val {
			gr.QueryData.Add(k, v)
		}
	} else {
		if queryVal, err := url.ParseQuery(content); err == nil {
			for k := range queryVal {
				gr.QueryData.Add(k, queryVal.Get(k))
			}
		} else {
			gr.Errors = append(gr.Errors, err)
		}
	}
	return gr
}

// Param accepts as Go conventions ; as a synonym for &. (https://github.com/golang/go/issues/2210)
// Thus, Query won't accept ; in a query string if we provide something like fields=f1;f2;f3
// This Param is then created as an alternative method to solve this.
func (gr *GoReq) Param(key string, value string) *GoReq {
	gr.QueryData.Add(key, value)
	return gr
}

// Socks5 sets SOCKS5 proxy. For exmaple:
//
// gr.Socks5()"tcp", PROXY_ADDR, nil, proxy.Direct)
// gr.Socks5("tcp", "127.0.0.1:8080",
//    &proxy.Auth{User:"username", Password:"password"},
//    &net.Dialer {
//        Timeout: 30 * time.Second,
//        KeepAlive: 30 * time.Second,
//    },
//)
//
func (gr *GoReq) Socks5(network, addr string, auth *proxy.Auth, forward proxy.Dialer) *GoReq {
	dialer, err := proxy.SOCKS5(network, addr, auth, forward)
	if err != nil {
		gr.Errors = append(gr.Errors, err)
	} else {
		gr.Transport.Dial = dialer.Dial
	}
	return gr
}

// Timeout is used to set timeout for connections.
func (gr *GoReq) SetTimeout(timeout time.Duration) *GoReq {
	gr.Transport.Dial = func(network, addr string) (net.Conn, error) {
		conn, err := net.DialTimeout(network, addr, timeout)
		if err != nil {
			gr.Errors = append(gr.Errors, err)
			return nil, err
		}
		conn.SetDeadline(time.Now().Add(timeout))
		return conn, nil
	}
	return gr
}

// TLSClientConfig is used to set TLSClientConfig for underling Transport.
// One example is you can use it to disable security check (https):
//
//      goreq.New().TLSClientConfig(&tls.Config{ InsecureSkipVerify: true}).
//        Get("https://disable-security-check.com").
//        End()
//
func (gr *GoReq) TLSClientConfig(config *tls.Config) *GoReq {
	gr.Transport.TLSClientConfig = config
	return gr
}

// Proxy function accepts a proxy url string to setup proxy url for any request.
// It provides a convenience way to setup proxy which have advantages over usual old ways.
// One example is you might try to set `http_proxy` environment. This means you are setting proxy up for all the requests.
// You will not be able to send different request with different proxy unless you change your `http_proxy` environment again.
// Another example is using Golang proxy setting. This is normal prefer way to do but too verbase compared to GoReq's Proxy:
//
//      goreq.New().Proxy("http://myproxy:9999").
//        Post("http://www.google.com").
//        End()
//
// To set no_proxy, just put empty string to Proxy func:
//
//      goreq.New().Proxy("").
//        Post("http://www.google.com").
//        End()
//
func (gr *GoReq) Proxy(proxyURL string) *GoReq {
	parsedProxyURL, err := url.Parse(proxyURL)
	if err != nil {
		gr.Errors = append(gr.Errors, err)
	} else if proxyURL == "" {
		gr.Transport.Proxy = nil
	} else {
		gr.Transport.Proxy = http.ProxyURL(parsedProxyURL)
	}
	return gr
}

// RedirectPolicy is used to set redirect policy.
func (gr *GoReq) RedirectPolicy(policy func(req Request, via []Request) error) *GoReq {
	gr.CheckRedirect = func(r *http.Request, v []*http.Request) error {
		vv := make([]Request, len(v))
		for i, r := range v {
			vv[i] = Request(r)
		}
		return policy(Request(r), vv)
	}
	if gr.Client != nil {
		gr.Client.CheckRedirect = gr.CheckRedirect
	}
	return gr
}

// SendStruct (similar to SendMapString) returns *GoReq's itself for any next chain and takes content interface{} as a parameter.
// Its duty is to transfrom interface{} (implicitly always a struct) into s.Data (map[string]interface{}) which later changes into appropriate format such as json, form, text, etc. in the End() func.
// You can pass a struct to it:
//      type BrowserVersionSupport struct {
//        Chrome string
//        Firefox string
//      }
//      ver := BrowserVersionSupport{ Chrome: "37.0.2041.6", Firefox: "30.0" }
//      goreq.New().
//        Post("/update_version").
//        SendStruct(ver).
//        SendStruct(`{"Safari":"5.1.10"}`).
//        End()
func (gr *GoReq) SendStruct(content interface{}) *GoReq {
	if marshalContent, err := json.Marshal(content); err != nil {
		gr.Errors = append(gr.Errors, err)
	} else {
		var val map[string]interface{}
		d := json.NewDecoder(bytes.NewBuffer(marshalContent))
		d.UseNumber()
		if err := d.Decode(&val); err != nil {
			gr.Errors = append(gr.Errors, err)
		} else {
			for k, v := range val {
				gr.Data[k] = v
			}
		}
	}
	return gr
}

// SendMapString returns *GoReq's itself for any next chain and takes content string as a parameter.
// Its duty is to transform json String or query Strings into s.Data (map[string]interface{}) which later changes into appropriate format such as json, form, text, etc. in the End func.
// SendMapString function accepts either json string or other strings which is usually used to assign data to POST or PUT method.
// you can pass a json string:
//
//      goreq.New().
//        Post("/search").
//        SendMapString(`{ "query": "sushi" }`).
//        End()
//
// Or a query string:
//
//      goreq.New().
//        Post("/search").
//        SendMapString("query=tonkatsu").
//        End()
// You can also do multiple chain of Send:
//
//      goreq.New().
//        Post("/search").
//        SendMapString("query=bicycle&size=50x50").
//        SendMapString(`{ "wheel": "4"}`).
//        End()
func (gr *GoReq) SendMapString(content string) *GoReq {
	var val map[string]interface{}
	// check if it is json format
	d := json.NewDecoder(strings.NewReader(content))
	d.UseNumber()
	if err := d.Decode(&val); err == nil {
		for k, v := range val {
			gr.Data[k] = v
		}
	} else if formVal, err2 := url.ParseQuery(content); err2 == nil {
		for k := range formVal {
			// make it array if already have key
			if val, ok := gr.Data[k]; ok {
				var strArray []string
				strArray = append(strArray, formVal.Get(k))
				// check if previous data is one string or array
				switch oldValue := val.(type) {
				case []string:
					strArray = append(strArray, oldValue...)
				case string:
					strArray = append(strArray, oldValue)
				}
				gr.Data[k] = strArray
			} else {
				// make it just string if does not already have same key
				gr.Data[k] = formVal.Get(k)
			}
		}
		if gr.Header["Content-Type"] == "" {
			gr.Header["Content-Type"] = "application/x-www-form-urlencoded"
		}

	} else {
		// need to add text mode or other format body request to this func instead of an error
		gr.RawStringData = content
	}
	return gr
}

// SendRawString returns *GoReq's itself for any next chain and takes content string as a parameter.
// Its duty is to transform String into gr.RawStringData and send raw string in request body.
func (gr *GoReq) SendRawString(content string) *GoReq {
	if gr.Header["Content-Type"] == "" {
		gr.Header["Content-Type"] = "text/plain"
	}
	gr.RawStringData = content
	return gr
}

// SendRawBytes returns *GoReq's itself for any next chain and takes content string as a parameter.
// Its duty is to transform []byte into gr.RawBytesData and send raw bytes in request body.
func (gr *GoReq) SendRawBytes(content []byte) *GoReq {
	if gr.Header["Content-Type"] == "" {
		gr.Header["Content-Type"] = "application/octet-stream"
	}
	gr.RawBytesData = content
	return gr
}

// SendFile posts a file to server.
func (gr *GoReq) SendFile(paramName, filePath string) *GoReq {
	gr.FileParam = paramName
	gr.FilePath = filePath
	return gr
}

//copy from https://matt.aimonetti.net/posts/2013/07/01/golang-multipart-file-upload-example/
func newfileUploadRequest(gr *GoReq, params map[string]string, paramName, filePath string) (*bytes.Buffer, error) {
	file, err := os.Open(filePath)
	if err != nil {
		return nil, err
	}
	fileContents, err := ioutil.ReadAll(file)
	if err != nil {
		return nil, err
	}
	fi, err := file.Stat()
	if err != nil {
		return nil, err
	}
	file.Close()

	body := new(bytes.Buffer)
	writer := multipart.NewWriter(body)
	part, err := writer.CreateFormFile(paramName, fi.Name())
	if err != nil {
		return nil, err
	}
	part.Write(fileContents)

	for key, val := range params {
		_ = writer.WriteField(key, val)
	}
	err = writer.Close()
	if err != nil {
		return nil, err
	}

	gr.Header["Content-Type"] = writer.FormDataContentType()
	return body, nil
}

func changeMapToURLValues(data map[string]interface{}) url.Values {
	var newURLValues = url.Values{}
	for k, v := range data {
		switch val := v.(type) {
		case string:
			newURLValues.Add(k, val)
		case []string:
			for _, element := range val {
				newURLValues.Add(k, element)
			}
		// if a number, change to string
		// json.Number used to protect against a wrong (for GoReq) default conversion
		// which always converts number to float64.
		// This type is caused by using Decoder.UseNumber()
		case json.Number:
			newURLValues.Add(k, string(val))
		}
	}
	return newURLValues
}

func changeMapToMapString(data map[string]interface{}) map[string]string {
	var m map[string]string

	for k, v := range data {
		switch val := v.(type) {
		case string:
			m[k] = val
		case []string:
			m[k] = strings.Join(val, ",")
		// if a number, change to string
		// json.Number used to protect against a wrong (for GoReq) default conversion
		// which always converts number to float64.
		// This type is caused by using Decoder.UseNumber()
		case json.Number:
			m[k] = string(val)
		}
	}
	return m
}

// BindBody set bind object for response.
//
// For example:
//    type Person struct {
//        Name string
//    }
//
//    var friend Person
//    response, _, errs := request.Post("http://example.com").BindBody(&friend).End()
//
func (gr *GoReq) BindBody(bindResponseBody interface{}) *GoReq {
	gr.bindResponseBody = bindResponseBody
	return gr
}

// End is the most important function that you need to call when ending the chain. The request won't proceed without calling it.
// End function returns Response which matchs the structure of Response type in Golang's http package (but without Body data). The body data itself returns as a string in a 2nd return value.
// Lastly but worth noticing, error array (NOTE: not just single error value) is returned as a 3rd value and nil otherwise.
//
// For example:
//
//    resp, body, errs := goreq.New().Get("http://www.google.com").End()
//    if (errs != nil) {
//      fmt.Println(errs)
//    }
//    fmt.Println(resp, body)
//
// Moreover, End function also supports callback which you can put as a parameter.
// This extends the flexibility and makegr *GoReq fun and clean! You can use GoReq in whatever style you love!
//
// For example:
//
//    func printBody(resp goreq.Response, body string, errs []error){
//      fmt.Println(resp.Status)
//    }
//    goreq.New().Get("http://www..google.com").End(printBody)
//
func (gr *GoReq) End(callback ...func(response Response, body string, errs []error)) (Response, string, []error) {
	var bytesCallback []func(response Response, body []byte, errs []error)
	if len(callback) > 0 {
		bytesCallback = []func(response Response, body []byte, errs []error){
			func(response Response, body []byte, errs []error) {
				callback[0](response, string(body), errs)
			},
		}
	}
	resp, body, errs := gr.EndBytes(bytesCallback...)
	if gr.bindResponseBody != nil {
		json.Unmarshal(body, gr.bindResponseBody)
	}
	bodyString := string(body)
	return resp, bodyString, errs
}

// EndBytes should be used when you want the body as bytes. The callbacks work the same way as with `End`, except that a byte array is used instead of a string.
func (gr *GoReq) EndBytes(callback ...func(response Response, body []byte, errs []error)) (Response, []byte, []error) {
	var (
		req  *http.Request
		err  error
		resp Response
	)
	// check whether there is an error. if yes, return all errors
	if len(gr.Errors) != 0 {
		return nil, nil, gr.Errors
	}

	switch gr.Method {
	case POST, PUT, PATCH:
		if gr.Header["Content-Type"] == "" {
			gr.Header["Content-Type"] = "application/json"
		}

		if gr.FilePath != "" { //post a file
			buf, _ := newfileUploadRequest(gr, changeMapToMapString(gr.Data), gr.FileParam, gr.FilePath)
			req, err = http.NewRequest(gr.Method, gr.URL, buf)
		} else if gr.Header["Content-Type"] == "application/json" && len(gr.Data) > 0 { //json
			contentJSON, _ := json.Marshal(gr.Data)
			contentReader := bytes.NewReader(contentJSON)
			req, err = http.NewRequest(gr.Method, gr.URL, contentReader)
		} else if gr.Header["Content-Type"] == "application/x-www-form-urlencoded" { //form
			formData := changeMapToURLValues(gr.Data)
			req, err = http.NewRequest(gr.Method, gr.URL, strings.NewReader(formData.Encode()))
		} else if len(gr.RawBytesData) > 0 { //raw bytes
			req, err = http.NewRequest(gr.Method, gr.URL, bytes.NewReader(gr.RawBytesData))
		} else { //raw string
			req, err = http.NewRequest(gr.Method, gr.URL, strings.NewReader(gr.RawStringData))
		}
	case GET, HEAD, DELETE, OPTIONS:
		req, err = http.NewRequest(gr.Method, gr.URL, nil)

	default:
		gr.Errors = append(gr.Errors, errors.New("No method specified"))
		return nil, nil, gr.Errors
	}
	initRequest(req, gr)

	// Log details of this request
	if gr.Debug {
		dump, err := httputil.DumpRequest(req, true)
		gr.logger.SetPrefix("[http] ")
		if err != nil {
			gr.logger.Printf("Error: %s", err.Error())
		}
		gr.logger.Printf("HTTP Request: %s", string(dump))
	}

	if gr.CurlCommand {
		curl, err := http2curl.GetCurlCommand(req)
		gr.logger.SetPrefix("[curl] ")
		if err != nil {
			gr.logger.Println("Error:", err)
		} else {
			gr.logger.Printf("CURL command line: %s", curl)
		}
	}

	// Send request
	resp, err = gr.retryDo(req, gr.retry.RetryCount)

	// Log details of this response
	if gr.Debug {
		dump, err := httputil.DumpResponse(resp, true)
		if nil != err {
			gr.logger.Println("Error: ", err.Error())
		}
		gr.logger.Printf("HTTP Response: %s", string(dump))
	}

	if err != nil {
		gr.Errors = append(gr.Errors, err)
		return nil, nil, gr.Errors
	}
	defer resp.Body.Close()

	body, _ := ioutil.ReadAll(resp.Body)
	// Reset resp.Body so it can be use again
	resp.Body = ioutil.NopCloser(bytes.NewBuffer(body))
	// deep copy response to give it to both return and callback func
	respCallback := *resp
	if len(callback) != 0 {
		callback[0](&respCallback, body, gr.Errors)
	}
	return resp, body, nil
}

func initRequest(req *http.Request, gr *GoReq) {
	//bind host
	req.Host = gr.Host
	for k, v := range gr.Header {
		req.Header.Set(k, v)
	}
	// Add all querystring from Query func
	q := req.URL.Query()
	for k, v := range gr.QueryData {
		for _, vv := range v {
			q.Add(k, vv)
		}
	}
	req.URL.RawQuery = q.Encode()

	// Add basic auth
	if gr.BasicAuth != (struct{ Username, Password string }{}) {
		req.SetBasicAuth(gr.BasicAuth.Username, gr.BasicAuth.Password)
	}

	// Add cookies
	for _, cookie := range gr.Cookies {
		req.AddCookie(cookie)
	}

	//check client
	if gr.Client == nil {
		gr.setDefaultClient()
	}
	if gr.CheckRedirect != nil {
		gr.Client.CheckRedirect = gr.CheckRedirect
	}

	// Set Transport
	gr.Client.Transport = gr.Transport
}

// Retry is used to retry to send requests if servers return unexpected status.
// So GoReq tries at most retryCount + 1 times and request interval is retryTimeout.
// You can indicate which status GoReq should retry in case of. If it is nil, retry only when status code >= 400
//
// For example:
//    _, _, err := New().Get("http://example.com/a-wrong-url").
//    Retry(3, 100, nil).
//    End()
//
func (gr *GoReq) Retry(retryCount int, retryTimeout int, retryOnHTTPStatus []int) *GoReq {
	gr.retry = &RetryConfig{RetryCount: retryCount, RetryTimeout: retryTimeout, RetryOnHTTPStatus: retryOnHTTPStatus}
	return gr
}

func (gr *GoReq) retryDo(req *http.Request, retryCount int) (resp Response, err error) {
	r, err := gr.Client.Do(req)

	if retryCount == 0 {
		resp = r
		return
	}

	if gr.retry.RetryOnHTTPStatus == nil {
		if r.StatusCode >= 200 {
			resp = r
			return
		}

		resp, err = gr.retryDo(req, retryCount-1)
	} else {
		for _, s := range gr.retry.RetryOnHTTPStatus {
			if r.StatusCode == s {
				if gr.retry.RetryTimeout > 0 {
					time.Sleep(time.Duration(gr.retry.RetryTimeout) * time.Second)
				}
				resp, err = gr.retryDo(req, retryCount-1)
				return
			}
		}
		// none of the statuses for which we want to retry - pass the response on as is
		resp = r
	}
	return
}

// CustomMethod : Just a wrapper to initialize SuperAgent instance by method string
func (gr *GoReq) CustomMethod(method, targetURL string) *GoReq {
	switch method {
	case POST:
		return gr.Post(targetURL)
	case GET:
		return gr.Get(targetURL)
	case HEAD:
		return gr.Head(targetURL)
	case PUT:
		return gr.Put(targetURL)
	case DELETE:
		return gr.Delete(targetURL)
	case PATCH:
		return gr.Patch(targetURL)
	case OPTIONS:
		return gr.Options(targetURL)
	default:
		gr.Reset()
		gr.Method = method
		gr.URL = targetURL
		gr.Errors = nil
		return gr
	}
}
