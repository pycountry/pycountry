with import <nixpkgs> {}; {
	env = stdenv.mkDerivation {
	name = "env";
	buildInputs = [ gettext ];

	};
}
