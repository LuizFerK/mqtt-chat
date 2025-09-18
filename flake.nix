{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            python311
            python311Packages.paho-mqtt
            docker-compose
            docker
          ];

          shellHook = ''
            echo "Available commands:"
            echo "  nix run .#start-all           # Start all services"
            echo "  nix run .#start-broker        # Start MQTT broker"
            echo "  nix run .#stop-broker         # Stop MQTT broker"
            echo "  nix run .#restart-broker      # Restart MQTT broker"
            echo "  nix run .#cleanup             # Cleanup all services"
            echo "  nix run .#status              # Check broker status"
            echo "  nix run .#logs                # View broker logs"
            echo "  nix run .#run-app             # Run the chat application"
          '';
        };

        packages = {
          start-broker = pkgs.writeShellScriptBin "start-broker" ''
            ${pkgs.docker-compose}/bin/docker-compose up -d
            echo "Broker available at: localhost:1883"
            echo "WebSocket available at: localhost:9001"
          '';

          stop-broker = pkgs.writeShellScriptBin "stop-broker" ''
            ${pkgs.docker-compose}/bin/docker-compose down
          '';

          restart-broker = pkgs.writeShellScriptBin "restart-broker" ''
            ${pkgs.docker-compose}/bin/docker-compose restart
          '';

          logs = pkgs.writeShellScriptBin "logs" ''
            ${pkgs.docker-compose}/bin/docker-compose logs -f
          '';

          status = pkgs.writeShellScriptBin "status" ''
            ${pkgs.docker-compose}/bin/docker-compose ps
          '';

          run-app = pkgs.writeShellScriptBin "run-app" ''
            ${pkgs.python311}/bin/python main.py
          '';

          # Combined script to start everything
          start-all = pkgs.writeShellScriptBin "start-all" ''
            if ! ${pkgs.docker}/bin/docker info > /dev/null 2>&1; then
              echo "Docker is not running. Please start Docker first."
              exit 1
            fi
            
            ${pkgs.docker-compose}/bin/docker-compose up -d
            sleep 3
            
            if ${pkgs.docker-compose}/bin/docker-compose ps | grep -q "Up"; then
              ${pkgs.python311}/bin/python main.py
            else
              echo "Failed to start MQTT broker"
              echo "Check logs with: nix run .#logs"
              exit 1
            fi
          '';

          cleanup = pkgs.writeShellScriptBin "cleanup" ''
            ${pkgs.docker-compose}/bin/docker-compose down -v
          '';
        };

        apps = {
          start-broker = flake-utils.lib.mkApp { drv = self.packages.${system}.start-broker; };
          stop-broker = flake-utils.lib.mkApp { drv = self.packages.${system}.stop-broker; };
          restart-broker = flake-utils.lib.mkApp { drv = self.packages.${system}.restart-broker; };
          logs = flake-utils.lib.mkApp { drv = self.packages.${system}.logs; };
          status = flake-utils.lib.mkApp { drv = self.packages.${system}.status; };
          install-deps = flake-utils.lib.mkApp { drv = self.packages.${system}.install-deps; };
          run-app = flake-utils.lib.mkApp { drv = self.packages.${system}.run-app; };
          start-all = flake-utils.lib.mkApp { drv = self.packages.${system}.start-all; };
          cleanup = flake-utils.lib.mkApp { drv = self.packages.${system}.cleanup; };
        };
      });
}
