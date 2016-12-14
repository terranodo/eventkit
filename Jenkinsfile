node('sl61') {
  stage 'Checkout'
  checkout scm

  stage 'Test'
  sh """
  uname -r
  livecd-creator
  """
}
