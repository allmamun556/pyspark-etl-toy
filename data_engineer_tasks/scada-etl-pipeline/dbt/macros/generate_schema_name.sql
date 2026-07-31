{#
    dbt's default behavior concatenates the target schema and a model's
    custom +schema config (e.g. "public_marts"). We want clean, predictable
    schema names instead ("staging", "marts") so the pipeline's curated
    tables in "public" stay visibly separate from dbt's own output.
#}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
