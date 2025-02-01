{% macro lower_and_unaccent_array(column_name) %}
array(
    select trim(replace(lower(unaccent(value::text)), '"',''))
    from unnest({{ column_name }}) as value
)
{% endmacro %}

REPLACE(tracker.streets, '"', '')