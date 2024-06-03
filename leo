#! /bin/sh -
# POSIX-compliant wrapper script that executes $(basename $0).py
# Allows you to put symlinks (even differently named ones) to this script in
# any directory (e.g. /usr/local/bin), but the venv will still be created in
# the directory of the resolved symlink (the regular file).

set -eEu # exit on error, inherit that property to functions, unset variables are error

# POSIX trap doesn't have the ERR trap
trap '[ $? = 0 ] || echo "There was an error executing '"'"'$0'"'"'"' EXIT

# Bit overkill, but needed: https://stackoverflow.com/a/33266819/13823467
rreadlink()(set +eu; target=$1 fname= targetDir= CDPATH=; { \unalias command; \unset -f command; } >/dev/null 2>&1; [ -n "${ZSH_VERSION}" ] && options[POSIX_BUILTINS]=on; while :; do [ -L "$target" ] || [ -e "$target" ] || { command printf '%s\n' "ERROR: '$target' does not exist." >&2; return 1; }; command cd "$(command dirname -- "$target")"; fname=$(command basename -- "$target"); [ "$fname" = '/' ] && fname=''; if [ -L "$fname" ]; then target=$(command ls -l "$fname"); target=${target#* -> }; continue; fi; break; done; targetDir=$(command pwd -P); if [ "$fname" = '.' ]; then command printf '%s\n' "${targetDir%/}"; elif  [ "$fname" = '..' ]; then command printf '%s\n' "$(command dirname -- "${targetDir}")"; else command printf '%s\n' "${targetDir%/}/$fname"; fi)

realpath="$(rreadlink "$0")"
prefix="$(dirname -- "${realpath}")"

log () {
	case "$1" in
		err)  clr="31"    ;;
		warn) clr="33"    ;;
		info) clr="34"    ;;
		*)    clr="41;30" ;;
	esac
	printf "\033[${clr}m$0: %s\033[m\n" "$2"
}

# try python3 -m venv and virtualenv to create venv,
# then activate and install requirements.txt
create_env () {
	rm -rf "${prefix}"/env
	command -v python3 >/dev/null 2>&1 || { log err "failed to find python3."; exit 2; }
	python3 -m venv "${prefix}/env" || virtualenv --python "$(command -v python3)" "${prefix}/env"
	command . "${prefix}"/env/bin/activate || { log err "failed to activate venv."; exit 3; }
	pip3 install -r "${prefix}"/requirements.txt || { log err "failed to install dependencies."; exit 4; }
}

# Activate venv -- dot builtin should be called with command builtin: https://unix.stackexchange.com/a/740901/520093
command . "${prefix}"/env/bin/activate || { log warn "failed to activate venv. Creating it."; create_env; }

# Exec script with args
exec "${prefix}"/$(basename -- "${realpath}").py "$@"
