{% macro match_with_null_check(a_column, b_column) %}
    (
        {{ b_column }} is null or {{ a_column }} = {{ b_column }} or {{ a_column }} is null
    )
{% endmacro %}
