#!/usr/bin/env bash

# shellcheck disable=SC2207

base_url="https://github.com/${user_name}/${repo_name}"
pkg_path=$(pwd)
distro=$(uname)             # Linux / Darwin
arch=$(uname -m)            # x86_64 / aarch64 / arm64

help() {
	echo -e "USAGE\n\t$(basename $0) <options>"
	echo -e "OPTIONS"
	echo -e "\t-h --help\tShow this help message and exit"
	echo -e "\t-u --user\tGithub user name"
	echo -e "\t-r --repo\tGithub repo name"
	echo -e "\t-t --type\tPackage type (deb, rpm, tar.gz)"
}

if [[ $# -eq 0 ]]; then
    help
    exit 1
fi

while (( $# )); do
	key="$1"
	case $key in
		-h|--help)
			help
			exit 0
			;;
		-u|--user)
			user_name="$2"
			shift 2
			;;
		-r|--repo)
			repo_name="$2"
			shift 2
			;;
		-t|--type)
			pkg_type="$2"
			shift 2
			;;
		*)
			help
			;;
	esac
done

latest=$(curl -s "$base_url/releases" | awk -F '[<>]' "/\/${user_name}\/${repo_name}\/releases\/tag\// {print \$5}" | head -n 1)

pkg_urls=($(curl -s "https://api.github.com/repos/${user_name}/${repo_name}/releases/latest" \
	| awk "/browser_download_url/ && /${pkg_type}/ && /${latest}/ { print }" \
	| cut -d : -f 2,3 \
	| tr -d \" \
	| sed 's/^ *//g'
))

check_pkg() {
    if [[ -z "${pkg_urls[*]}" ]]; then
        echo "No packages found for $pkg_type"
        exit 1
    fi

	exclusions=("md5")

	pkg_urls_string=$(printf "%s\n" "${pkg_urls[@]}")

	for exclusion in "${exclusions[@]}"; do
		pkg_urls_string=$(echo "$pkg_urls_string" | grep -vF "$exclusion")
	done

	readarray -t pkg_urls <<< "$pkg_urls_string"

    if [[ "${#pkg_urls[@]}" -gt 1 ]]; then
        pkg_url=$(echo "${pkg_urls[@]}" | tr ' ' '\n' | grep -iE "${distro}|${arch}")
    fi

    if [[ -z "$pkg_url" ]]; then
        echo "No packages found for $distro/$arch"
        echo -e "Available packages:\n"
        count=1
        for pkg in "${pkg_urls[@]}"; do
            echo "$count: $pkg"
            count=$((count+1))
        done
        read -rp "Enter package number: " pkg_num
        pkg_url="${pkg_urls[$pkg_num]}"
    fi

}

dl_pkg() {
	curl -s -L -o "$1" "$2"
}

main() {
    check_pkg
    local pkg_name="${pkg_url##*/}"
    local output="${pkg_path}/${pkg_name}"
    dl_pkg "$output" "$pkg_url"
    echo "$pkg_name downloaded to $pkg_path"
}

main "$@"

exit 0
