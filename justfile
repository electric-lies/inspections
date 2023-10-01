prod_build version:
  docker build . --tag inspections_backend:{{version}}
  docker tag inspections_backend:{{version}} electriclies/inspections:1.0
  docker push electriclies/inspections:1.0
