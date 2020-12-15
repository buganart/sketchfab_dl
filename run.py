#!/usr/bin/env python3
from pathlib import Path
from multiprocessing.pool import ThreadPool

import click

import auth
from download import download_model
import search


def unpack_args(fun):
    def decorated(args):
        return fun(*args)

    return decorated


@unpack_args
def download(uid, path):
    path.mkdir(parents=True, exist_ok=True)
    download_model(uid, str(path))


@click.command()
@click.option("--count", "-c", default=10)
@click.option("--query", "-q", required=True)
@click.option("--num-threads", "-n", default=5)
@click.option("--output-dir", "-o", default="models")
def main(count, query, num_threads, output_dir):

    pool = ThreadPool(num_threads)

    with open("api_token.txt") as f:
        token = f.read().strip()

    auth.set_api_token(token)

    # Search parameters see: https://docs.sketchfab.com/data-api/v3/index.html#/search
    params = {"type": "models", "q": query, "downloadable": True, "count": count}

    # Get a collection of models from the search API
    models = search.search_results(params)
    print(f"Found {len(models)} models.")
    if len(models) == 0:
        print("No models found")
    else:
        pool.map(
            download,
            [(model["uid"], Path(output_dir) / model["uid"]) for model in models],
        )


if __name__ == "__main__":
    main()
