permissions:
  contents: read

jobs:
  your-job-name:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          repository: psanogo/cobalt_sandbox
          # ... other options
