{ pkgs }: {
  deps = [
    pkgs.python312Full
    pkgs.python312Packages.pip
    pkgs.python312Packages.setuptools
    pkgs.python312Packages.wheel
    pkgs.python312Packages.requests
    pkgs.python312Packages.pandas
    pkgs.python312Packages.numpy
    pkgs.python312Packages.python-dotenv
  ];
}