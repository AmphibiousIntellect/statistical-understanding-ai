#' Profile a data frame without modifying it.
#'
#' @param data A data.frame.
#' @return A named list of JSON-friendly summaries.
#' @export
profile_data <- function(data) {
  if (!is.data.frame(data)) {
    stop("data must be a data.frame", call. = FALSE)
  }

  duplicate_rows <- duplicated(data) | duplicated(data, fromLast = TRUE)
  list(
    row_count = nrow(data),
    column_count = ncol(data),
    columns = names(data),
    types = vapply(data, function(column) class(column)[[1]], character(1)),
    missing_count = vapply(data, function(column) sum(is.na(column)), integer(1)),
    unique_count = vapply(
      data,
      function(column) length(unique(column)),
      integer(1)
    ),
    duplicate_row_count = sum(duplicate_rows)
  )
}

#' Inspect a data frame without applying transformations.
#'
#' @param data A data.frame.
#' @return A list containing a profile and findings.
#' @export
inspect_data <- function(data) {
  data_profile <- profile_data(data)
  findings <- list()

  if (data_profile$duplicate_row_count > 0) {
    findings[[1]] <- list(
      code = "duplicate_rows",
      severity = "warning",
      status = "needs_context",
      message = paste(
        data_profile$duplicate_row_count,
        "rows participate in exact duplicate groups."
      ),
      evidence = list(duplicate_row_count = data_profile$duplicate_row_count),
      statistical_implication = paste(
        "Deleting legitimate repeated observations can change sample size,",
        "variance estimates, and the analysis population."
      ),
      proposed_action = paste(
        "Review the observational unit, candidate key, and repeat structure",
        "before deciding whether any row is redundant."
      )
    )
  }

  list(profile = data_profile, findings = findings)
}
