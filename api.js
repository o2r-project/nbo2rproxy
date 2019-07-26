const Docker = require('dockerode');
const docker = new Docker({ socketPath: '/var/run/docker.sock' });

// run nested container on API request
const path = require('path');
const express = require('express');
const responseTime = require('response-time');
const bodyParser = require('body-parser');
const randomstring = require('randomstring');
const Stream = require('stream');

app_dir = path.dirname(path.resolve(__dirname));
console.log('[o2r-api] o2r app root: %s', app_dir);

const baseUrl = process.env.BASE_URL || '/';
const serverUrl = baseUrl + 'o2r';
const port = parseInt(process.env.O2R_API_PORT || '4242');

const app = express();
app.use(responseTime());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// curl -X POST -d '{data: 'value'}' localhost:4242/v1/run
app.post('/v1/run', function (req, res) {
    console.log('[o2r-api]', req.url);
    compendium_path = process.env.ERC_PATH;
    console.log('[o2r-api] executing ERC at ', compendium_path);
    execute(compendium_path, res);
});

// http://localhost:4242/v1/status
app.get('/v1/status', function (req, res) {
  res.setHeader('Content-Type', 'application/json');
  res.send({
    o2r: 'status',
    port: port
  });
});

const server = app.listen(port, () => {
    console.log('[o2r-api] o2r API waiting for requests on port', port);

    console.log('[o2r-api] run a container')
    // simple Docker run
    docker
    .run('ubuntu', ['bash', '-c', 'echo "[nested container] $(uname -a) | user: $(whoami) | user ID: $UID" '], process.stdout)
    .then(function (container) {
        console.log('[app.js] container ID:    ', container.id);
        console.log('[app.js] container status:', container.output.StatusCode);
        return container.remove();
    }).then(function (data) {
        console.log('[app.js] container removed');
    }).catch(function (err) {
        console.log(err);
    });
});

// function testing the core interaction of the container: reading a mounted directory and writing to it
// *******
// PROBLEM: the directory path is on the host! need to be told the directory from outside, and need to read up on mounting directories to binder (see roadmap)
// *******
execute = function (compendium_path, response) {
    console.log('[o2r-api] execute with ', compendium_path)
    let res = response;

    let create_options = {
        CpuShares: 128,
        Env: ['nbo2rproxy=true'],
        Memory: 1073741824, // 1G
        MemorySwap: 2147483648, // 2 * Memory
        User: '1000',
        name: 'o2r_manifest_' + randomstring.generate(3),
        HostConfig: {
            Binds: [compendium_path + ':' + '/erc'],
            AutoRemove: false
        }
    };

    let start_options = {};
    
    r_render_command = 'containerit::CMD_Rscript(basename(\'/erc/main.Rmd\'), vanilla = TRUE)';
    r_dockerfile_command = 'containerit::dockerfile('
        + 'from = \'/erc/main.Rmd\', image = \'rocker/geospatial:3.5.1\', '
        + 'maintainer = \'nbo2rproxy\', '
        + 'copy = NA, '
        + 'container_workdir = \'/erc\', '
        + 'cmd = ' + r_render_command + ')';
    r_command = 'setwd(\'/erc\'); write(' + r_dockerfile_command + ')';
    let cmd = ['Rscript', '-e', r_command ];

    console.log('[o2r-api] Starting Docker container', create_options.name, 'now with cmd ', cmd);

    let log = [];
    const containerLogStream = Stream.Writable();
    containerLogStream._write = function (chunk, enc, next) {
      msg = Buffer.from(chunk).toString().trim();
      console.log('[container]', msg);
      log.push(msg);
      next();
    };

    docker.run('o2rproject/containerit:geospatial-0.5.0', cmd, containerLogStream, create_options, start_options, (err, data, container) => {
        console.log('[o2r-api] container running', container);
        if (err) {
            console.error(err);
        } else {
            if (data.StatusCode === 0) {
                console.log('[o2r-api] Completed metadata extraction:', JSON.stringify(data));
                res.status(200).send({success: data, log: log});
            } else {
                console.log('[o2r-api] Error: ', JSON.stringify(data));
                res.status(500).send({error: data, log: log});
            }
        }
    });
}
