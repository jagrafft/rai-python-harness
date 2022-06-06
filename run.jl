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

using Dates: format, now
using Logging
using RAI: Context, HTTPError, load_config

include("harness/helpers.jl")
include("harness/parseargs.jl")

# Call to `main()` on last line of script
function main()
    args = parseargs(
        "config", Dict(:help => "TOML configuration file, e.g. 'config.toml'", :required => true, :arg_type => String),
        "--database", Dict(:help => "database name (default: config['database'])", :arg_type => String),
        "--engine", Dict(:help => "engine name (default: config['engine'])", :arg_type => String),
        "--profile", Dict(:help => "RAI Cloud profile (default: default)", :arg_type => String))
    try
        run_harness(args.config, args.database, args.engine; profile = args.profile)
        exit()
    catch e
        println(e)
        # e isa HTTPError ? show(e) : rethrow()
    end
end

function dispatch_query(context, database, engine, query)
    @info "dispatch_query" ts=now() database=database engine=engine
    @info "post" query_type=query["type"]
end

function run_harness(config_file, database, engine; profile)
    # Load TOML configuration file
    configuration = load_toml(config_file)
    validate_configuration(configuration, config_file)

    # set database and engine
    rai_database = database == nothing ? configuration["database"] : database
    rai_engine = engine == nothing ? configuration["engine"] : engine

    # Initialize output path
    output_path = dirname(abspath(config_file))
    # Use different part of path depending on whether 'config_file' is local to `run.jl`
    output_suffix = string(occursin("/", config_file) ? dirname(config_file) : split(basename(config_file), ".")[1])
    output_dir = "$(output_path)/output-$(output_suffix)" 

    # Initialize target directory
    init_ts = format(now(), "YYYY-mm-ddTHHMMSS")
    init_or_reset_target_dir(output_dir, init_ts)

    # Initiatlize logger
    log_file = open("$(output_dir)/log-$(init_ts).txt", "w+")
    logger = SimpleLogger(log_file)
    global_logger(logger)

    @info "Begin RAI operations..." ts=now()
    @info "Initiate connection to RAI KGMS..." ts=now()
    @info profile=profile
    rai_config = load_config(; profile=profile)
    rai_context = Context(rai_config)

    # Iterate 'queries' array and execute queries
    for query in configuration["queries"]
        @info "pre" query_type=query["type"]

        # Convert query type to uppercase
        query["type"] = uppercase(query["type"])
        dispatch_query(rai_context, rai_database, rai_engine, query)
    end

    @info "Run complete" ts=now()
    close(log_file)
end 

# Run program
main()
