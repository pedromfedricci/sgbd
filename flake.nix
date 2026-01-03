{
  description = "A digital library management service";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  };

  outputs = {
    self,
    nixpkgs,
  }: let
    system = "x86_64-linux";
    pkgs = import nixpkgs {inherit system;};
  in {
    devShells.${system}.default = pkgs.mkShell {
      packages = with pkgs; [
        python314
        uv
        just
        docker
        hurl
      ];

      LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
        pkgs.stdenv.cc.cc
      ];

      shellHook = ''
        export LD_LIBRARY_PATH=$LD_LIBRARY_PATH
      '';
    };
  };
}
