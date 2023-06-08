from click import ClickException


def _check_package_id(arguments, client):
    if not arguments.get('package_id'):
        raise ClickException(
            'No required package_id found in .connect_deployment.yaml file.',
        )

    if client.extensions.objects.filter(
        package_id=arguments.get('package_id'),
        deleted_at__isnull=True,
    ).exists():
        raise ClickException(
            f'Extension with package_id {arguments["package_id"]} already exists.',
        )