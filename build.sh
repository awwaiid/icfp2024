#!/bin/bash

pip install -r requirements.txt

echo "Setting up ocaml and opam in asdf"
(asdf plugin-list | grep ocaml) || asdf plugin-add ocaml
(asdf plugin-list | grep opam)  || asdf plugin-add opam https://github.com/asdf-community/asdf-opam.git

asdf install

