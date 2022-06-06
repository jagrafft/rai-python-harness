# Copyright 2022 RelationalAI, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License

using Dates: now
using TOML: parsefile

const REQUIRED_CONFIG_KEYS = [ "authors", "create_database", "data_dir", "database", "description", "engine", "project", "source_dir", "version_control", "queries" ]
const REQUIRED_CONFIG_QUERY_KEYS = [ "file_name", "index", "type" ] 

function init_or_reset_target_dir(path, ts)
    # Rename existing directory if necessary
    if isdir(path)
        try
            Base.Filesystem.mv(path, "$(path)-$(ts)")
        catch e
            println(e)
        end
    end

    # Create directory for current output
    try
        Base.Filesystem.mkdir(path)
    catch e
        println(e)
    end
end

function load_toml(config)
    try
        parsefile(config)
    catch e
        println(e isa Base.TOML.ParserError ? "Error in TOML File" : e)
    end
end

function validate_configuration(config, file_name)
    # Ensure confifguration file contains required global keys #
    # Collect missing keys
    missing_keys = reduce((a,c) -> (
        if !haskey(config, c)
            push!(a,c);
        end;
        return a
    ), REQUIRED_CONFIG_KEYS, init=[])

    # Report missing keys to user, if they exist
    if length(missing_keys) > 0
        println("ERROR: $(file_name) missing keys [$(join(missing_keys,", "))]")
        exit()
    end

    # Ensure that config["version_control"]["url"] exists and is populated
    if !haskey(config["version_control"], "url")
        print("ERROR: $(file_name)['version_control'] missing 'url' key")
        exit()
    end

    if length(config["version_control"]["url"]) < 1
        print("ERROR: $(file_name)['version_control']['url'] is empty")
        exit()
    end

    # Ensure that config["queries"] is correctly formatted #
    # Ensure indices are unique
    query_indices = map(x -> (
        if !haskey(x[2], "index")
            println("ERROR: table at position $(x[1]) in $(file_name)['queries'] missing 'index' key");
            exit();
        else
            x[2]["index"]
        end;
    ), enumerate(config["queries"]))

    if length(query_indices) != length(Set(query_indices))
        print("ERROR: Duplicate 'index' in $(file_name)['queries']")
        exit()
    end

    # Collect missing keys in query tables
    invalid_query_tables = reduce((a,c) -> (
        for k in REQUIRED_CONFIG_QUERY_KEYS
            if !haskey(c,k)
                push!(a, "index $(c["index"]) missing key '$(k)'");
            end;
        end;
        return a
    ), config["queries"], init=[])

    # Report missing keys to user
    if length(invalid_query_tables) > 0
        println("ERROR: $(file_name)['queries'] contains one or more invalid tables")
        foreach(e -> println("  - $(e)"), invalid_query_tables)
        exit()
    end
end
