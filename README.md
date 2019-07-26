# nbo2rproxy

**Goal**

Run a small HTML app that starts a container within the Jupyter instance.
The nested container is started via `Dockerode` from a Node.js app - just like the [o2r reference implementation]().

The realisation is modelled after [`nbstencilaproxy`](https://github.com/minrk/nbstencilaproxy).

The first step is to only use `start` and `postBuild` scripts, leaving many bits hard-coded.

**Try it**

You need a `repo2docker` fork that allows execution as `root` user, see https://github.com/o2r-project/repo2docker/tree/allow_root

```
repo2docker --debug --volume=/var/run/docker.sock:/var/run/docker.sock --env ERC_PATH=$(pwd)/erc --user-id=0 --user-name=root .
```

Then open the UI at `/o2r-ui` or via the "New > ERC" menu, or inspect the API at `/o2r-api/v1/status`.

You can query the API directly if you provide the token and adjust the port:

```
curl http://127.0.0.1:53889/o2r-api/v1/status/?token=2d77384eb9cbb8190b06709cc790b0bf441de3b25ec6ffee
```

**Open questions**

- How can the volume mount of the ERC be automated?
- Is this really feasible, given that I trust the users who are allowed to open a repository on Binder (i.e. I know who they are, and normally I control the repository content, too)?
- What changes need to be made to this kind of repository and image to work on JupyterHub?
