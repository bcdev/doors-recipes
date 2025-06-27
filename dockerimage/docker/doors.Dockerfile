FROM quay.io/bcdev/xcube:v1.9.0

LABEL maintainer="xcube-team@brockmann-consult.de"

RUN echo "xcube version: v1.9.0"; \
    echo "xcube cmems version: 0.1.5"; \
    echo "geodb version: 1.0.9"; \
    echo "geodb places plugin version: 0.0.4"; \
    echo "vdc places plugin version: 0.1}"; \
    echo "reference stores version: 0.1.5}";

RUN micromamba install -y -n base -c conda-forge python=3.11 xcube-cmems=0.1.5 "copernicusmarine<=1.3.5" xcube_geodb=1.0.9 xcube_places_plugin=0.0.4

RUN micromamba install -y -n base -c conda-forge xcube=1.9.0 xvec pip "botocore<1.36" "numcodecs<=0.16"

RUN micromamba run -n base python3 -m pip install --no-deps https://github.com/xcube-dev/xcube-vdc-places/archive/v0.1.tar.gz

RUN micromamba run -n base python3 -m pip install --no-deps https://github.com/bcdev/doors-stores/archive/v0.1.5.tar.gz

ENTRYPOINT ["/usr/local/bin/_entrypoint.sh"]

# Default command (shell form)
CMD xcube --help