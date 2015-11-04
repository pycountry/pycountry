with import <nixpkgs> {}; {
	env = stdenv.mkDerivation {
	name = "env";
	buildInputs = [ gettext python27 python34 ];
       shellHook =  ''
         if [ ! -d bin ];
         then
           virtualenv --python=python2.7 .
         fi
	 if [ ! -e bin/buildout ];
	 then
		bin/pip install zc.buildout
	 fi
	 bin/buildout
       ''
       ;

	};
}
