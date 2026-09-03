source(file.path("..", "..", "R", "core.R"))

fixture <- file.path("..", "..", "..", "fixtures", "duplicate_rows.csv")

testthat::test_that("profile_data reports the shared fixture", {
  data <- read.csv(fixture, na.strings = "", stringsAsFactors = FALSE)
  result <- profile_data(data)

  testthat::expect_equal(result$row_count, 4)
  testthat::expect_equal(result$column_count, 3)
  testthat::expect_equal(result$columns, c("participant_id", "visit", "value"))
  testthat::expect_equal(unname(result$missing_count[["value"]]), 2)
  testthat::expect_equal(result$duplicate_row_count, 2)
})

testthat::test_that("inspect_data proposes review without mutating", {
  data <- read.csv(fixture, na.strings = "", stringsAsFactors = FALSE)
  before <- data
  result <- inspect_data(data)

  testthat::expect_identical(data, before)
  testthat::expect_length(result$findings, 1)
  testthat::expect_equal(result$findings[[1]]$code, "duplicate_rows")
  testthat::expect_equal(result$findings[[1]]$status, "needs_context")
})
