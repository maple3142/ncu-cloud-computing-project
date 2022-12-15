const http = require('http')

http.createServer((req, res) => {
	const host = req.headers['host']
	if (host == 'localhost') {
		res.end(`Flag: ${process.env.FLAG}`)
	} else {
		res.end(`Host: ${host}`)
	}
}).listen(8000)
